#!/usr/bin/env python3
"""
ONE-SHOT rewrite of the five location pages into genuinely distinct pages.

Run once. Re-running is harmless (the replacements no longer match and it reports
"0 changes"), but it will NOT preserve hand edits made afterwards — once the review
placeholders are filled in by hand, treat the HTML as the source of truth and this
script as history.

WHY: Google indexed 3 of 38 URLs. The five location pages measured 93.5% identical on
body copy and 99.6% identical once the city name was masked out — i.e. one template,
five times. That is a doorway-page signal.

WHAT STAYS SHARED (deliberately — these are the same business and the same services):
nav, footer, NAP block, trust bar, services grid, comparison section, review carousel,
Instagram embed, contact form, pricing, and the LocalBusiness core fields.

WHAT IS UNIQUE PER PAGE:
title, meta description, OG/Twitter, H1, opening section, "Serving X" section, FAQs
(visible + JSON-LD, generated from one source so they cannot drift), the per-page
Service schema node, and image alt text.

HONEST FRAMING: no page claims a location in its city. Every page says the service is
mobile, run out of 2336 Noble Road in Raleigh, and states the approximate drive.
Do not add city addresses or city phone numbers.

GEOGRAPHY SOURCE: neighborhoods, roads and landmarks below are general knowledge of the
Triangle, not client-supplied. They are real places, but they have NOT been confirmed
against where Tang actually takes jobs. See README-LOCATION-PAGES.md.
"""

import re
import sys
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# --------------------------------------------------------------------------------------
# PER-CITY CONTENT
# --------------------------------------------------------------------------------------
# Rules followed when writing this:
#   * No sentence appears on two pages. Not "no near-duplicates" — no shared sentences.
#   * Each opening takes a DIFFERENT ANGLE, so the pages don't read as one essay with the
#     nouns swapped: Cary = planned/HOA communities, Durham = old tree cover + campus
#     parking, Wake Forest = distance north and driveway space, Apex = small-town downtown
#     + family vehicles, Chapel Hill = tree canopy + campus/hills.
#   * Drive times are approximate and hedged ("about", "roughly"). They are off-peak
#     estimates from 2336 Noble Road. Nothing promises an arrival time.
#   * Superlatives removed. The old block said "Rated #1 Mobile Detailer in <City>, NC"
#     with no awarding body on all five pages. Replaced with the numbers that are actually
#     verifiable: 5.0 rating, 150+ Google reviews, 2,000+ vehicles.

CITIES = {
    "cary": {
        "city": "Cary",
        "drive": "about 25 minutes",
        "route": "Wade Avenue to I-440 and I-40",
        "title": "Mobile Detailing Cary NC — We Come to You | Tang Detailing",
        "desc": "Mobile detailing, paint correction and ceramic coating across Cary — Preston, Lochmere, Amberly and Weycroft. We come to you, about 25 min from our Raleigh shop.",
        "og_title": "Mobile Detailing in Cary, NC — Tang Detailing Comes to You",
        "og_desc": "Detailing and ceramic coating at your Cary driveway or office lot. Roughly 25 minutes from our Raleigh shop. 5.0\u2605 \u00b7 150+ Google reviews.",
        "tw_desc": "Detailing and ceramic coating brought to your driveway in Cary, NC.",
        "h1": "Mobile detailing in <em>Cary</em>, done in your driveway",
        "hero_tag": "We load the water, the power and the polishers. You keep your Saturday.",
        "hero_sub": "Full details, paint correction and ceramic coating, brought to Cary from our shop in Raleigh.",
        "hero_alt": "Ceramic coated car detailed by Tang Detailing for a client in Cary NC",
        "visual_alt": "Tang Detailing mobile setup working on a client vehicle in a Cary NC driveway",
        "eyebrow": "Serving Cary",
        "opening_h2": "Cary is a town of <em>tidy driveways</em>",
        "bullets": [
            "Your HOA keeps the street immaculate and your car is the one thing letting it down",
            "The commute down I-40 or NC-55 coats the front end in road film every week",
            "You park at Fenton or Waverly Place and come back to a fresh door ding and a dusty hood",
            "The tunnel wash off Kildaire Farm Road left you swirl marks under every streetlight",
            "You have wanted this handled for months and never once had a free Saturday",
        ],
        "opening_paras": [
            "Cary was largely built at once, and it shows \u2014 Preston, Lochmere, MacGregor Downs and Weycroft are neighborhoods where the lawns are edged and the mailboxes match. A car with water spots and a dull hood stands out on a street like that in a way it would not somewhere else.",
            "Most of our Cary work happens in exactly those driveways, plus the office lots off Weston Parkway and Harrison Avenue while our clients are inside working. We are a mobile operation running out of a shop at 2336 Noble Road in Raleigh, and Cary is <b>about 25 minutes away</b> for us on a normal morning \u2014 Wade Avenue, onto I-440, out I-40. We bring our own water and power, so all we need from you is the car and a place to stand.",
        ],
        "area_h2": "The parts of <em>Cary</em> we cover",
        "area_lead": "We are mobile, so this is a drive-to list rather than a branch list \u2014 everything here is a normal run for us from Raleigh.",
        "areas": [
            ("Preston &amp; MacGregor Downs", "Established west Cary"),
            ("Lochmere &amp; Regency Park", "Off Kildaire Farm Rd"),
            ("Amberly &amp; Cary Park", "Near Green Level"),
            ("Weycroft &amp; Carpenter Village", "North Cary"),
            ("Downtown Cary &amp; Academy St", "Near the Cary Park"),
            ("Morrisville &amp; Davis Drive", "On the RTP side"),
        ],
        "area_close": "If you are near the Cary/Apex line or over toward Morrisville, you are still well inside our normal range \u2014 ask when you book.",
        "faq_lead": "Cary-specific questions we get asked before booking.",
        "faqs": [
            ("How far is Cary from your shop?",
             "Our shop is at 2336 Noble Road in Raleigh, and most of Cary is <b>about 25 minutes</b> from there \u2014 Wade Avenue to I-440, then out I-40. West Cary neighborhoods like Amberly and Cary Park run a little longer. We are a mobile service, so we build that drive into the schedule rather than charging you for it."),
            ("Which parts of Cary do you actually cover?",
             "All of it, plus the edges. We regularly work in Preston, MacGregor Downs, Lochmere, Regency Park, Weycroft, Carpenter Village, Amberly, Cary Park and around downtown Cary and Academy Street, and we cross into Morrisville and out toward Davis Drive without any trouble."),
            ("Will your setup be a problem with my HOA?",
             "It has not been so far. We work out of one vehicle, we are not running a loud generator for hours, and we bring our own water rather than running a hose across a shared lawn. A full detail in a Cary driveway looks like a van parked at your curb for a few hours. If your HOA has a written rule about contractor vehicles, tell us when you book and we will work around it."),
            ("Can you detail my car at the office instead of at home?",
             "Yes, and in Cary that is roughly half of what we do. The office lots along Weston Parkway, Harrison Avenue and the Regency Park area work well for us \u2014 you hand over the keys, go back inside, and the car is finished by the time you leave. We just need a parking space we can work around, not a reserved bay."),
        ],
        "svc_desc": "Mobile auto detailing, paint correction and ceramic coating delivered to homes and office lots throughout Cary, NC \u2014 including Preston, MacGregor Downs, Lochmere, Weycroft, Amberly and Cary Park \u2014 by a Raleigh-based mobile detailing service roughly 25 minutes away.",
    },

    "durham": {
        "city": "Durham",
        "drive": "about 30 minutes",
        "route": "I-40 to the Durham Freeway",
        "title": "Durham Mobile Detailing & Ceramic Coating | Tang Detailing",
        "desc": "We detail cars at homes and offices across Durham \u2014 Trinity Park, Hope Valley, Woodcroft and RTP. Fully mobile from our Raleigh shop, about 30 minutes out.",
        "og_title": "Durham Mobile Car Detailing & Ceramic Coating \u2014 Tang Detailing",
        "og_desc": "Paint correction and ceramic coating at your Durham home or office. Roughly 30 minutes from our Raleigh shop. 5.0\u2605 \u00b7 150+ Google reviews.",
        "tw_desc": "Mobile detailing and ceramic coating for Durham, NC \u2014 we travel to the car.",
        "h1": "<em>Durham</em> mobile detailing &amp; ceramic coating, at your curb",
        "hero_tag": "Street parking, shade trees and sap. We deal with all three.",
        "hero_sub": "A full mobile setup that comes to Durham from our Raleigh shop \u2014 water, power and pro-grade product included.",
        "hero_alt": "Paint correction work by Tang Detailing on a vehicle in Durham NC",
        "visual_alt": "Tang Detailing client vehicle after a full detail at a home in Durham NC",
        "eyebrow": "Serving Durham",
        "opening_h2": "Durham parks its cars <em>under trees</em>",
        "bullets": [
            "Sap and pollen bake onto the hood every spring under the Trinity Park oaks",
            "Street parking downtown means you inherit whatever the car beside you drips",
            "The Durham Freeway commute leaves a film that a $12 wash does not touch",
            "Your clear coat has picked up water spots that no longer rinse off",
            "You are on campus or at RTP all day and there is never a window to deal with it",
        ],
        "opening_paras": [
            "Durham has the tree cover that Raleigh's newer suburbs do not, and paint pays for it. Trinity Park, Forest Hills, Watts-Hillandale and Old West Durham are full of hundred-year-old hardwoods sitting directly over the street, and the cars underneath collect sap, pollen and bird traffic in a way that garage-kept cars never do. Left alone through a summer, that etches.",
            "That is most of what we are hired for here \u2014 decontamination and correction on paint that has been living outdoors, then a coating so the next season does less damage. We run out of a shop at 2336 Noble Road in Raleigh and Durham is <b>about 30 minutes</b> out for us, I-40 to the Durham Freeway. We arrive with our own water and power, which matters on a Durham street where there is nowhere to plug in.",
        ],
        "area_h2": "Where in <em>Durham</em> we work",
        "area_lead": "We are a Raleigh-based mobile service, so treat this as the list of places we drive to \u2014 there is no Durham shop to visit.",
        "areas": [
            ("Trinity Park &amp; Old West Durham", "Near Ninth Street"),
            ("Forest Hills &amp; Hope Valley", "South Durham"),
            ("Duke Park &amp; Watts-Hillandale", "North of downtown"),
            ("Woodcroft &amp; Southpoint", "Off 15-501"),
            ("Downtown &amp; American Tobacco", "Street &amp; deck parking"),
            ("Research Triangle Park", "Office lots"),
        ],
        "area_close": "Working on campus, in an apartment deck or at an RTP office lot is fine \u2014 tell us the parking situation when you book and we will plan around it.",
        "faq_lead": "What Durham clients ask us before the first appointment.",
        "faqs": [
            ("Do you actually drive out to Durham?",
             "Yes. We are based at 2336 Noble Road in Raleigh and Durham is <b>roughly 30 minutes</b> away \u2014 out I-40, then onto the Durham Freeway. It is one of our regular runs, not an exception we make. There is no Durham storefront; the whole service comes to wherever the car is parked."),
            ("Which Durham neighborhoods do you serve?",
             "Trinity Park, Old West Durham, Forest Hills, Hope Valley, Duke Park, Watts-Hillandale, Woodcroft, the Southpoint area, downtown and out into Research Triangle Park. If you are closer to Hillsborough or Chapel Hill than to central Durham, we still come \u2014 just say so when you book."),
            ("My car sits under trees and has sap and pollen baked on. Can that be fixed?",
             "Usually, yes, and it is a large share of our Durham work. Fresh sap and pollen come off with a proper decontamination wash and a chemical or clay treatment. Sap that has sat through a hot month often etches into the clear coat, and that needs machine polishing rather than washing. We will tell you honestly which one you are looking at before we start."),
            ("Can you work at my office in RTP or near Duke?",
             "Yes, and it is often easier than a home visit. An open lot space at an RTP office is ideal. Near Duke and downtown we can work from street parking or a deck level as long as there is room to open the doors and walk around the car \u2014 send us a photo of the spot if you are not sure and we will tell you before we drive out."),
        ],
        "svc_desc": "Mobile car detailing, paint decontamination, paint correction and ceramic coating for Durham, NC \u2014 covering Trinity Park, Forest Hills, Hope Valley, Duke Park, Woodcroft and Research Triangle Park \u2014 provided from a Raleigh shop approximately 30 minutes away.",
    },

    "wake-forest": {
        "city": "Wake Forest",
        "drive": "about 25 minutes",
        "route": "Falls of Neuse Road or Capital Boulevard",
        "title": "Wake Forest Mobile Detailing at Your Home | Tang Detailing",
        "desc": "Detailing and ceramic coating brought to Wake Forest driveways \u2014 Heritage, Traditions, Holding Village. Roughly 25 minutes north of our Raleigh shop.",
        "og_title": "Mobile Detailing in Wake Forest, NC \u2014 Tang Detailing",
        "og_desc": "We drive north to Wake Forest \u2014 Heritage, Traditions, Holding Village and Caveness Farms. Detailing and ceramic coating at your home. 5.0\u2605 \u00b7 150+ reviews.",
        "tw_desc": "Detailing and ceramic coating brought north to Wake Forest, NC driveways.",
        "h1": "Ceramic coating &amp; mobile detailing, delivered to <em>Wake Forest</em>",
        "hero_tag": "You already drive far enough. We will come to you.",
        "hero_sub": "A complete mobile detailing setup, roughly 25 minutes north of our Raleigh shop.",
        "hero_alt": "Freshly detailed vehicle by Tang Detailing at a home in Wake Forest NC",
        "visual_alt": "Tang Detailing working on a client SUV in a Wake Forest NC driveway",
        "eyebrow": "Serving Wake Forest",
        "opening_h2": "In Wake Forest, the <em>driveway is the advantage</em>",
        "bullets": [
            "You already commute south every morning and are not spending a Saturday driving again",
            "Capital Boulevard construction grit ends up down the whole side of the car",
            "Two kids, a dog and a school run have happened to your back seat",
            "The car lives outside because the garage holds everything except the car",
            "You want the coating done properly rather than a wax that lasts three washes",
        ],
        "opening_paras": [
            "Wake Forest is far enough north that everything is a drive \u2014 which is exactly why a mobile detailer makes more sense here than almost anywhere else we serve. Nobody in Heritage or Traditions wants to add another trip down US-1 to their week just to get the car cleaned, and the newer neighborhoods off Rogers Road and Ligon Mill have the one thing our job actually needs: a long, flat, private driveway with room to work around the whole vehicle.",
            "So we drive to you. Our shop is at 2336 Noble Road in Raleigh and Wake Forest is <b>about 25 minutes</b> up Falls of Neuse Road or Capital Boulevard, depending on where you sit. We bring water, power and everything else in the van. You leave the car outside and carry on with your morning.",
        ],
        "area_h2": "<em>Wake Forest</em> areas we drive to",
        "area_lead": "A mobile route, not a branch network \u2014 our only location is the Raleigh shop, and these are the stops we make from it.",
        "areas": [
            ("Heritage", "Off Rogers Rd"),
            ("Traditions &amp; Caveness Farms", "North Wake Forest"),
            ("Holding Village", "Near the lake"),
            ("Downtown &amp; White Street", "Historic district"),
            ("Bowling Green &amp; Olde Mill Stream", "Near NC-98"),
            ("Rolesville &amp; Youngsville", "Just past town"),
        ],
        "area_close": "Wakefield and the North Raleigh neighborhoods along Falls of Neuse are on the way for us, so they book on the same runs.",
        "faq_lead": "Questions from Wake Forest clients, answered.",
        "faqs": [
            ("Is Wake Forest too far for a mobile detailer?",
             "Not for us. It is <b>about 25 minutes</b> from our shop at 2336 Noble Road in Raleigh, straight up Falls of Neuse Road or Capital Boulevard. Wake Forest is one of the areas we drive to most, partly because so many homes here have the driveway space that makes a full mobile detail straightforward."),
            ("Which Wake Forest areas do you cover?",
             "Heritage, Traditions, Caveness Farms, Holding Village, Bowling Green, Olde Mill Stream, the historic downtown and White Street area, and out to Rolesville and Youngsville. Wakefield and the North Raleigh neighborhoods along Falls of Neuse are effectively on the way, so those fit the same route."),
            ("What do you need from me in the driveway?",
             "Space to walk all the way around the car with the doors open, and the keys. That is genuinely it \u2014 we carry our own water tank and power, so we are not running your hose or your outdoor outlet. Most Wake Forest driveways have more than enough room; a two-car driveway with the second car moved out is ideal."),
            ("Can you do a ceramic coating outside rather than in a shop?",
             "Yes, with one condition: coatings need a dry, stable window to cure properly, so we schedule them around the weather rather than pushing through it. We do the decontamination and paint correction first, apply the coating in your driveway, and tell you exactly how long to keep the car dry afterwards. If the forecast turns, we would rather move the appointment than rush a coating that has to last years."),
        ],
        "svc_desc": "Mobile detailing, paint correction and ceramic coating brought to driveways across Wake Forest, NC \u2014 including Heritage, Traditions, Holding Village, Caveness Farms and the White Street historic district \u2014 from a Raleigh shop roughly 25 minutes south.",
    },

    "apex": {
        "city": "Apex",
        "drive": "about 30 minutes",
        "route": "I-440 to US-1 south",
        "title": "Apex NC Mobile Detailing & Paint Correction | Tang Detailing",
        "desc": "Paint correction, ceramic coating and full details in Apex \u2014 Scotts Mill, Haddon Hall, Sweetwater. We travel to you from Raleigh, about 30 minutes.",
        "og_title": "Apex, NC Mobile Detailing & Paint Correction \u2014 Tang Detailing",
        "og_desc": "Full details and ceramic coating at your Apex home \u2014 Scotts Mill, Haddon Hall, Shepherd's Vineyard and Sweetwater. 5.0\u2605 \u00b7 150+ Google reviews.",
        "tw_desc": "Full details, paint correction and ceramic coating at your home in Apex, NC.",
        "h1": "Your <em>Apex</em> driveway is our mobile detailing bay",
        "hero_tag": "No drop-off, no loaner, no lost afternoon.",
        "hero_sub": "Full details, paint correction and ceramic coating, driven out to Apex from our Raleigh shop.",
        "hero_alt": "Vehicle detailed by Tang Detailing at a residence in Apex NC",
        "visual_alt": "Tang Detailing full detail in progress on a family SUV in Apex NC",
        "eyebrow": "Serving Apex",
        "opening_h2": "Apex cars carry <em>a lot of life</em>",
        "bullets": [
            "The back seat has crumbs, juice and something that has been there since spring break",
            "Weekend trips toward Jordan Lake come home with sand in every footwell",
            "The US-64 and NC-55 run has left a haze of road film across the paint",
            "Salem Street parking is tight and your doors have paid for it",
            "You want it done at the house, not dropped somewhere for a whole day",
        ],
        "opening_paras": [
            "Apex still behaves like a small town at the center \u2014 Salem Street, the old depot, people walking to dinner \u2014 wrapped in subdivisions full of families. That mix shows up in the cars. A lot of what we clean here is not neglect, it is a three-row SUV that has done school runs, a Jordan Lake weekend and a Costco trip in the same seven days, with car seats that have not come out since they went in.",
            "Interiors are the bigger half of the job in Apex for that reason, usually paired with correction work on paint that has spent a couple of years outdoors. We are mobile and our only location is the shop at 2336 Noble Road in Raleigh, so we come to Scotts Mill, Haddon Hall, Sweetwater or wherever you are \u2014 <b>about 30 minutes</b> for us down US-1. Everything arrives in the van, including the water.",
        ],
        "area_h2": "<em>Apex</em> neighborhoods we serve",
        "area_lead": "We travel to all of these from Raleigh. There is no Apex location \u2014 the van is the location.",
        "areas": [
            ("Scotts Mill &amp; Salem Village", "Central Apex"),
            ("Haddon Hall &amp; Abbington", "Off the Peakway"),
            ("Sweetwater &amp; Riley's Pond", "West Apex"),
            ("Shepherd's Vineyard", "Near Olive Chapel"),
            ("Historic Downtown &amp; Salem St", "Tight parking, still fine"),
            ("Beaver Creek &amp; Holly Springs edge", "South of US-64"),
        ],
        "area_close": "If you sit closer to Holly Springs, New Hill or the Cary line, that is the same trip for us \u2014 mention it when you book.",
        "faq_lead": "The Apex questions that come up most.",
        "faqs": [
            ("How long does it take you to get to Apex?",
             "<b>About 30 minutes</b> from our shop at 2336 Noble Road in Raleigh \u2014 I-440 round to US-1 south. West Apex out toward Olive Chapel Road runs a few minutes longer. We are fully mobile, so that drive is ours to absorb, not something added to your quote."),
            ("What parts of Apex do you serve?",
             "Scotts Mill, Salem Village, Haddon Hall, Abbington, Sweetwater, Riley's Pond, Shepherd's Vineyard, the Villages of Apex and the historic downtown around Salem Street. We also pick up jobs toward Beaver Creek and over the Holly Springs and New Hill lines on the same runs."),
            ("Our SUV has car seats and years of kid damage. Is that a problem?",
             "No \u2014 in Apex it is close to the default job. We would rather you leave the car seats in than wrestle them out, though taking them out does let us get properly underneath. Crumbs, spills, dried juice and ground-in snacks all come out with a hot water extractor and steam. Tell us what we are walking into when you book so we schedule enough time rather than rushing the interior."),
            ("Can you work near downtown Apex where parking is tight?",
             "Usually. Around Salem Street and the depot we need a space where the doors open fully and we can walk the perimeter of the car, which a normal street space often does not give us. If you live or work right in the historic center, the simplest fix is to point us at a driveway or a lot nearby \u2014 send a photo of the spot and we will confirm before the appointment."),
        ],
        "svc_desc": "Mobile interior and exterior detailing, paint correction and ceramic coating for Apex, NC \u2014 serving Scotts Mill, Salem Village, Haddon Hall, Sweetwater, Shepherd's Vineyard and the Salem Street historic district \u2014 from a Raleigh-based shop about 30 minutes away.",
    },

    "chapel-hill": {
        "city": "Chapel Hill",
        "drive": "about 35 minutes",
        "route": "I-40 to US-15-501",
        "title": "Chapel Hill Mobile Auto Detailing | Tang Detailing",
        "desc": "Mobile auto detailing for Chapel Hill \u2014 Meadowmont, Southern Village, Glen Lennox and near UNC. About 35 minutes from our Raleigh shop, and we come to you.",
        "og_title": "Chapel Hill Mobile Auto Detailing & Ceramic Coating \u2014 Tang Detailing",
        "og_desc": "We drive to Chapel Hill \u2014 Meadowmont, Southern Village, Glen Lennox, Coker Hills and the UNC campus area. 5.0\u2605 \u00b7 150+ Google reviews.",
        "tw_desc": "Mobile auto detailing and ceramic coating for Chapel Hill, NC and Carrboro.",
        "h1": "<em>Chapel Hill</em> car detailing, without leaving your driveway",
        "hero_tag": "The farthest we drive, and worth it every time.",
        "hero_sub": "Detailing, correction and coating brought over from our Raleigh shop \u2014 roughly 35 minutes.",
        "hero_alt": "Detailed and ceramic coated vehicle by Tang Detailing in Chapel Hill NC",
        "visual_alt": "Tang Detailing client car after paint correction at a home in Chapel Hill NC",
        "eyebrow": "Serving Chapel Hill",
        "opening_h2": "Chapel Hill's <em>tree canopy</em> is hard on paint",
        "bullets": [
            "Oak and pine cover means sap, pollen and bird traffic almost year-round",
            "Campus and Franklin Street parking has cost you more than one door edge",
            "Shaded, damp driveways leave water spots that dry on instead of off",
            "The 15-501 commute films the front of the car in a week",
            "You have been meaning to protect the paint properly for two years now",
        ],
        "opening_paras": [
            "Chapel Hill is the greenest place we work and the hardest on a finish because of it. The canopy over Coker Hills, Lake Forest and the older streets near campus drops sap and pollen for most of the year, and driveways that never get direct sun stay damp long enough to leave mineral spotting rather than drying clean. Cars here rarely look neglected \u2014 they look shaded, spotted and slightly dull.",
            "The work that fixes that is decontamination, machine polishing and then a coating that gives the next few seasons something to land on instead of your clear coat. Chapel Hill is the <b>farthest we drive, about 35 minutes</b> from our shop at 2336 Noble Road in Raleigh, out I-40 and onto 15-501. We are entirely mobile \u2014 water, power and product all arrive with us, which matters on a hilly Chapel Hill driveway with no outdoor tap.",
        ],
        "area_h2": "Where we go in <em>Chapel Hill</em>",
        "area_lead": "Everything here is a drive from Raleigh. Tang Detailing has no Chapel Hill address \u2014 we bring the whole operation to the car.",
        "areas": [
            ("Meadowmont", "Off NC-54"),
            ("Southern Village", "South 15-501"),
            ("Glen Lennox &amp; Coker Hills", "Near campus"),
            ("Lake Forest &amp; Chapel Hill North", "North of town"),
            ("UNC campus &amp; Franklin Street", "Decks &amp; permit lots"),
            ("Carrboro &amp; Briar Chapel", "Including over the Chatham line"),
        ],
        "area_close": "Briar Chapel and Governors Club sit just over the Chatham County line but carry Chapel Hill addresses \u2014 we serve both on the same trip.",
        "faq_lead": "Chapel Hill questions, answered before you book.",
        "faqs": [
            ("Do you come all the way out to Chapel Hill?",
             "We do \u2014 it is the longest trip we make, <b>about 35 minutes</b> from our Raleigh shop at 2336 Noble Road, out I-40 and onto US-15-501. It is a standing part of our schedule rather than a favour, but it does mean Chapel Hill appointments are easier to fit earlier in the day. Book a little further ahead than you would in Raleigh."),
            ("Which Chapel Hill areas do you cover?",
             "Meadowmont, Southern Village, Glen Lennox, Coker Hills, Lake Forest, Chapel Hill North, the streets around campus and Franklin Street, and across into Carrboro. Briar Chapel and Governors Club are technically in Chatham County but have Chapel Hill addresses, and we serve both."),
            ("The trees here leave sap and spots on my paint. What actually removes it?",
             "Washing alone will not do it once sap has hardened or water spots have started to etch. The fix is a decontamination wash followed by machine polishing to level the affected clear coat, and then a ceramic coating so the next round of sap sits on the coating instead of your paint. Under a heavy canopy, the coating is the part that pays for itself."),
            ("Can you detail a car parked on campus or near Franklin Street?",
             "Sometimes, and it depends entirely on the space. We need room to open every door and walk around the vehicle, which permit lots usually allow and tight street parking on and around Franklin Street usually does not. Parking decks are workable on an end space. Send us a photo of where the car sits and we will tell you honestly before we make a 35-minute drive."),
        ],
        "svc_desc": "Mobile auto detailing, paint decontamination, machine paint correction and ceramic coating for Chapel Hill, NC \u2014 including Meadowmont, Southern Village, Glen Lennox, Coker Hills, Carrboro and Briar Chapel \u2014 delivered from a Raleigh shop roughly 35 minutes away.",
    },
}

# The one FAQ that is intentionally identical everywhere: the prices are the prices.
SHARED_PRICING_FAQ = (
    "How much does it cost?",
    "Standard service ranges $240\u2013$290, full details $240\u2013$390, exterior details from $150, "
    "and interior packages from $150. Ceramic coating is quoted per vehicle after we see the paint. "
    "Pricing is the same wherever we drive \u2014 we do not add a travel charge by city."
)


# --------------------------------------------------------------------------------------
# BUILDERS
# --------------------------------------------------------------------------------------

CHECK_SVG = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4">'
             '<path d="M20 6L9 17l-5-5"/></svg>')
PIN_SVG = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">'
           '<path d="M12 2C8 2 5 5 5 9c0 5 7 13 7 13s7-8 7-13c0-4-3-7-7-7z"/>'
           '<circle cx="12" cy="9" r="2.5"/></svg>')
ARROW_SVG = ('<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
             'stroke-width="2"><path d="M5 12h14M12 5l7 7-7 7"/></svg>')


def build_opening(c):
    bullets = "\n".join(
        f'          <li>{CHECK_SVG} {b}</li>' for b in c["bullets"]
    )
    paras = "\n".join(f'        <p class="pain-p">{p}</p>' for p in c["opening_paras"])
    return f'''<!-- ===================== OPENING / LOCAL INTRO ===================== -->
<!-- UNIQUE TO {c["city"].upper()}. Do not copy this block to another location page — the
     whole point of the 2026-09-04 rewrite is that no two location pages share a
     paragraph. If you need a section here on a new city page, write it from scratch. -->
<section class="surface-white pain-section">
  <div class="wrap">
    <div class="pain-top reveal">
      <div class="pain-badge">
        <div class="pain-badge-ring"></div>
        <div class="pain-badge-inner">
          <span class="pb-eyebrow">Rated</span>
          <span class="pb-num">5.0</span>
          <span class="pb-label">150+ Reviews</span>
        </div>
      </div>
      <div class="pain-top-copy">
        <!-- This used to read "Rated #1 Mobile Detailer in {c["city"]}, NC" on all five
             pages, with no awarding body behind it. Replaced with the numbers that can
             actually be checked against the Google profile. Do not put "#1" back. -->
        <h3>5.0&#9733; on Google across 150+ reviews</h3>
        <p>2,000+ vehicles detailed &middot; Mobile service to {c["city"]} from our Raleigh shop</p>
      </div>
    </div>
    <div class="pain-grid">
      <div class="pain-copy reveal d1">
        <h2 class="section-title">{c["opening_h2"]}</h2>
        <ul class="pain-list">
{bullets}
        </ul>
{paras}
        <a href="#contact" class="btn btn-primary btn-lg">Get Your {c["city"]} Quote {ARROW_SVG}</a>
      </div>
      <div class="pain-visual reveal d2">
        <picture>
          <source srcset="/assets/images/happy-clients.webp" type="image/webp">
          <img src="/assets/images/happy-clients.jpg" alt="{c["visual_alt"]}" width="4284" height="5712" loading="lazy">
        </picture>
      </div>
    </div>
  </div>
</section>'''


def build_area(c):
    tiles = "\n".join(
        f'          <div class="area-city">{PIN_SVG}<span><b>{name}</b><small>{note}</small></span></div>'
        for name, note in c["areas"]
    )
    return f'''<!-- ===================== SERVING {c["city"].upper()} ===================== -->
<!-- Neighborhood list is UNIQUE to this page. These are places we DRIVE to; the markup
     is deliberately <div>, not <a>, because there are no per-neighborhood pages and
     linking six fake URLs would be worse than not linking at all. -->
<section class="area-section">
  <div class="wrap">
    <div class="area-grid">
      <div class="reveal">
        <p class="area-eyebrow">{c["eyebrow"]}</p>
        <h2 class="section-title">{c["area_h2"]}</h2>
        <p class="section-lead">{c["area_lead"]}</p>
        <div class="area-cities">
{tiles}
        </div>
        <p class="area-note">{c["area_close"]}</p>
      </div>
      <div class="area-map reveal d1">
        <iframe title="Tang Detailing mobile service area \u2014 {c["city"]} and the Triangle, NC" src="https://www.google.com/maps/embed?pb=!1m14!1m12!1m3!1d209367.6!2d-78.78!3d35.86!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!5e0!3m2!1sen!2sus!4v1710000000000!5m2!1sen!2sus" loading="lazy" referrerpolicy="no-referrer-when-downgrade" allowfullscreen></iframe>
      </div>
    </div>
  </div>
</section>

<!-- ===================== LOCAL REVIEW ===================== -->
<!-- REVIEW PLACEHOLDER - {c["city"].upper()} - replace with real GBP review mentioning this city -->
<!-- Leave this commented-out block in place until a genuine review naming {c["city"]} exists
     on the Google profile. Do NOT paste in a review from another city and change the
     place name, and do not write one. An empty slot costs nothing; an invented review is
     a real problem. To publish: delete the two wrapper comment lines below. -->
<!-- BEGIN REVIEW BLOCK
<section class="surface-cream">
  <div class="wrap">
    <div class="sec-head center reveal">
      <p class="area-eyebrow" style="text-align:center;">From a {c["city"]} client</p>
      <h2 class="section-title">What {c["city"]} says</h2>
    </div>
    <blockquote class="local-review reveal d1">
      <p>REVIEW TEXT GOES HERE.</p>
      <cite>REVIEWER NAME &middot; {c["city"]}, NC</cite>
    </blockquote>
  </div>
</section>
END REVIEW BLOCK -->'''


def build_faq(c):
    faqs = c["faqs"] + [SHARED_PRICING_FAQ]
    items = []
    for q, a in faqs:
        items.append(
            f'      <div class="faq-item"><button class="faq-q">{q}<span class="ico"></span></button>'
            f'<div class="faq-a"><p>{a}</p></div></div>'
        )
    body = "\n".join(items)
    return f'''<!-- ===================== FAQ ===================== -->
<!-- {len(faqs)} questions, {len(c["faqs"])} of them written for {c["city"]} specifically.
     THE JSON-LD IN <head> MUST MATCH THIS LIST EXACTLY — Google treats FAQ schema that
     does not appear on the page as a structured-data violation. Both are generated from
     the same source in scripts/localize-pages.py, so edit them together or not at all. -->
<section id="faq" class="surface-white">
  <div class="wrap">
    <div class="sec-head center reveal">
      <h2 class="section-title">Questions, <em>answered</em></h2>
      <p class="section-lead" style="margin:0 auto;">{c["faq_lead"]}</p>
    </div>
    <div class="faq-list reveal d1" data-faq-group>
{body}
    </div>
  </div>
</section>'''


def strip_tags(s):
    return re.sub(r"<[^>]+>", "", s).replace("&amp;", "&").replace("&middot;", "·") \
            .replace("&#9733;", "★").replace("&rsquo;", "'")


def build_faq_schema(c):
    faqs = c["faqs"] + [SHARED_PRICING_FAQ]
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": strip_tags(q),
                "acceptedAnswer": {"@type": "Answer", "text": strip_tags(a)},
            }
            for q, a in faqs
        ],
    }


def build_service_schema(c, slug):
    """A per-page Service node.

    The AutoDetailing node is one business with one @id and is shared across all five
    pages by design — giving the same @id five different descriptions is what confuses
    a knowledge graph. So the per-page uniqueness lives here instead, on a Service node
    that legitimately differs by areaServed and points back at the shared business.
    """
    return {
        "@context": "https://schema.org",
        "@type": "Service",
        "@id": f"https://www.tangdetailing.com/mobile-detailing-{slug}#service",
        "name": f"Mobile Auto Detailing in {c['city']}, NC",
        "description": c["svc_desc"],
        "serviceType": "Mobile auto detailing, paint correction and ceramic coating",
        "provider": {"@id": "https://tangdetailing.com/#business"},
        "areaServed": {
            "@type": "City",
            "name": c["city"],
            "containedInPlace": {"@type": "State", "name": "North Carolina"},
        },
        "availableChannel": {
            "@type": "ServiceChannel",
            "serviceUrl": f"https://www.tangdetailing.com/mobile-detailing-{slug}",
            "servicePhone": "+19196706062",
        },
    }


# --------------------------------------------------------------------------------------
# APPLY
# --------------------------------------------------------------------------------------

def sub1(pattern, repl, s, label, flags=re.S):
    """Substitute exactly once, loudly. Silent no-op replacements are how these files
    drifted out of sync in the first place."""
    new, n = re.subn(pattern, lambda _m: repl, s, count=1, flags=flags)
    if n != 1:
        raise SystemExit(f"  !! FAILED: {label} (matched {n} times)")
    return new


def process(slug, c, dry=False):
    path = ROOT / f"mobile-detailing-{slug}.html"
    s = path.read_text(encoding="utf-8")
    orig = s
    url = f"https://www.tangdetailing.com/mobile-detailing-{slug}"

    # --- head: title + meta
    s = sub1(r"<title>.*?</title>", f"<title>{c['title']}</title>", s, "title")
    s = sub1(r'<meta name="description" content=".*?">',
             f'<meta name="description" content="{c["desc"]}">', s, "meta description")
    s = sub1(r'<meta property="og:title" content=".*?">',
             f'<meta property="og:title" content="{c["og_title"]}">', s, "og:title")
    s = sub1(r'<meta property="og:description" content=".*?">',
             f'<meta property="og:description" content="{c["og_desc"]}">', s, "og:description")
    s = sub1(r'<meta name="twitter:title" content=".*?">',
             f'<meta name="twitter:title" content="{c["og_title"]}">', s, "twitter:title")
    s = sub1(r'<meta name="twitter:description" content=".*?">',
             f'<meta name="twitter:description" content="{c["tw_desc"]}">', s, "twitter:description")

    # --- breadcrumb: was pointing at .html while the canonical is extensionless
    s = sub1(rf'"item": "https://tangdetailing\.com/mobile-detailing-{slug}\.html"',
             f'"item": "{url}"', s, "breadcrumb url")

    # --- FAQ schema, regenerated from the same source as the visible FAQ
    faq_json = json.dumps(build_faq_schema(c), indent=2, ensure_ascii=False)
    s = sub1(r'<script type="application/ld\+json">\s*\{\s*"@context": "https://schema\.org",\s*'
             r'"@type": "FAQPage".*?</script>',
             f'<script type="application/ld+json">\n{faq_json}\n</script>', s, "FAQ schema")

    # --- per-page Service node, injected ahead of the breadcrumb block
    svc_json = json.dumps(build_service_schema(c, slug), indent=2, ensure_ascii=False)
    anchor = "<!-- ===== BREADCRUMB ANCHOR ===== -->"
    s = sub1(r'<script type="application/ld\+json">\s*\{\s*"@context": "https://schema\.org",\s*'
             r'"@type": "BreadcrumbList"', anchor, s, "breadcrumb anchor")
    s = s.replace(
        anchor,
        "<!-- Per-page Service node. The description is unique per city; the business\n"
        "     itself deliberately stays a single entity at #business, because giving one\n"
        "     @id five different descriptions is what confuses a knowledge graph. -->\n"
        f"<script type=\"application/ld+json\">\n{svc_json}\n</script>\n\n"
        '<script type="application/ld+json">\n{\n  "@context": "https://schema.org",\n'
        '  "@type": "BreadcrumbList"',
        1,
    )

    # --- hero
    s = sub1(r"<h1>.*?</h1>", f'<h1>{c["h1"]}</h1>', s, "h1")
    s = sub1(r'<p class="hero-tag">.*?</p>', f'<p class="hero-tag">{c["hero_tag"]}</p>', s, "hero tag")
    s = sub1(r'<p class="hero-sub">.*?</p>', f'<p class="hero-sub">{c["hero_sub"]}</p>', s, "hero sub")
    s = sub1(r'(<img src="/assets/images/background\.1\.jpg" alt=")[^"]*(")',
             f'<img src="/assets/images/background.1.jpg" alt="{c["hero_alt"]}"', s, "hero alt")

    # --- body sections
    s = sub1(r'<!-- =+ CLIENT AVATAR / PAIN POINTS =+ -->\s*<section class="surface-white pain-section">.*?</section>',
             build_opening(c), s, "opening section")
    s = sub1(r'<section class="area-section">.*?</section>', build_area(c), s, "area section")
    s = sub1(r'<section id="faq" class="surface-white">.*?</section>', build_faq(c), s, "faq section")

    if dry:
        print(f"  (dry run) {slug}: would change {len(orig)} -> {len(s)} chars")
        return
    path.write_text(s, encoding="utf-8")
    print(f"  {slug:<14} {len(orig):>7} -> {len(s):>7} chars")


def main():
    dry = "--dry" in sys.argv
    print("Localizing five location pages" + (" (DRY RUN)" if dry else ""))
    for slug, c in CITIES.items():
        process(slug, c, dry)
    print("done")


if __name__ == "__main__":
    main()

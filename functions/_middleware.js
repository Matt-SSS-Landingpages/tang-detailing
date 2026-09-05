// Cloudflare Pages Function — runs on every request.
// Redirect the crawlable *.pages.dev preview host to the canonical custom domain
// so it can't compete for rankings / create duplicate content.
// Custom-domain requests (and anything else) pass straight through.
//
// Note: target is the www canonical host (matches every canonical tag, og:url,
// the sitemap, and the zone-level apex→www redirect). Using the bare apex here
// would force a double hop (pages.dev → apex → www).
export async function onRequest(context) {
  const { request, next } = context;
  const url = new URL(request.url);

  if (url.hostname.endsWith(".pages.dev")) {
    const location = `https://www.tangdetailing.com${url.pathname}${url.search}`;
    return Response.redirect(location, 301);
  }

  return next();
}

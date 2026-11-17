# asdaria

A lightweight consultancy site with eight static HTML pages, local assets and no runtime dependencies. The project name is **asdaria**.

The design uses an editorial consultancy layout with agricultural engineering and agribusiness positioning, authentic field photography, open service lists and clearly attributed project scopes. It avoids promotional statistics and implied endorsements.

The homepage opens with a deep-green hero that pairs the engineering and agribusiness proposition with a finished bakery interior, followed by the attributed organisation band, three practice areas linking straight to their services, three selected cases led by ASDARIA's own coffee commission, a count of the directors' assignments by practice area, and the reasons to work with ASDARIA alongside its directors. Content fades in once as it scrolls into view; nothing is hidden when JavaScript is unavailable or reduced motion is requested. About pairs the company statement with the four sectors named in the source document, then presents the two directors' portraits, the approach, a logo wall of organisations and future direction. The Services page opens with an index of all eight services, uses source photographs to connect production infrastructure, processing, post-harvest systems and enterprise support, and places each service's related experience under its heading. The Experience page organises all 56 entries into attributed sections: a dark band for the company assignment, practice tabs for the directors' assignments and a separate list for the directors' research. Each entry appears as a ruled row with its title beside its full description, and the coffee, Kalobeyei and AFPQ assignments appear as photographed or highlighted features. The gallery presents seven project photographs in an aligned grid. The Contact page keeps the phone number and email above the fold. Attribution sits in captions, section headings and project details, never in boxes over photographs. No images have been invented or substituted with stock imagery.

The site is light-only, including on devices set to dark mode. Forest green, olive and warm ivory establish the agricultural identity. The supplied full circular badge has a transparent background and sits beside a coordinated blue-grey ASDARIA wordmark and Agribzenergy Systems descriptor in the header. The compact footer carries a contact prompt with labelled call and email icons, the postal address and the privacy link; it does not repeat the header navigation. Its printed phone number is corrected to the approved +254733954103. The central emblem is retained as the favicon for legibility at small sizes. Matching line icons identify the service disciplines, sectors and experience groups. The full raster logo is available at `site\assets\asdaria-logo.png`; its detail is limited by the supplied image resolution.

## Local use

Requires Python 3.11 or newer. From this folder:

```powershell
python build.py
python serve.py
```

Open http://127.0.0.1:4173. Stop the server with Ctrl+C.

### Working on another computer

Clone https://github.com/ronaldndirangu/asdaria with Git, then work on a branch:

```powershell
git clone https://github.com/ronaldndirangu/asdaria.git
cd asdaria
git switch -c update-site
python build.py
python validate.py
python serve.py
```

After editing, rebuild and validate, commit the source changes and rendered pages, push the branch, and open a pull request targeting `main`. GitHub Actions requires the `Validate site` check before merging. Direct pushes, force pushes and deletion of `main` are blocked, including for administrators. No other reviewer's approval is required, so the repository owner can merge their own passing pull requests.

The local server explicitly serves WebP files as `image/webp`, so full-size photographs open in the browser even when Windows has no WebP MIME registration. It also sends the security headers from `site\_headers`, so local testing runs under the production content security policy. Like the recommended hosts, it answers missing addresses with `404.html` and status 404, and it sends `Cache-Control: no-cache` so the preview always shows the latest build.

`build.py` renders the HTML using `content.json`. Edit page copy in `build.py`, the service and experience register in `content.json`, and styles or interactions in `site\assets`. Rebuild after any of these changes: each page links the stylesheet and script with a content-hash version (`style.css?v=...`), so browsers fetch a changed file instead of reusing a cached copy, and `validate.py` fails when a page carries an outdated version. The rendered pages are included, so a host does not need Python.

Each project has a stable `id` and related `services`. Each service's `examples` references project IDs. These associations connect the service pages and experience register in both directions. The register has no search or filter controls. The directors' assignments sit under six practice tabs that follow the ARIA tabs pattern, with arrow, Home and End keys. A visible "Choose a practice area" label names the tabs, and every tab shows its assignment count. On wider screens the tabs sit in one row in a bar that sticks below the header; on phones all six show at once in an even grid that scrolls with the page. Each list except the last ends with a "Next practice" card that opens the following practice, so a reader can walk through all six in order. One practice shows at a time; the others use `hidden="until-found"`, so in-page Find in supporting browsers can reveal them. Links to an entry or practice (from Services, the homepage or a shared address) open the right tab and highlight the entry. Choosing a tab updates the address without adding history entries. Without JavaScript, all six practice lists appear one after another with their counts.

## Hosting

Deploy **only the contents of `site`**, with `index.html` at the deployment root. Do not upload this whole project, original materials or recovery artifacts. There are no secrets, build services, database requirements or environment variables. Hosts serve `404.html` at whatever address was requested, so it alone uses root-relative links (`/about.html`, `/assets/...`) and stays styled and navigable at nested addresses; this requires the site to sit at the domain root, not in a subfolder.

| Static hosting option | Build command | Publish directory |
| --- | --- | --- |
| Cloudflare Workers | None; add a `wrangler.jsonc` setting `assets.directory` to `./site` and `assets.not_found_handling` to `404-page`, then run `npx wrangler deploy` | `site` |
| Cloudflare Pages or Netlify | None for a direct upload | `site` |
| Firebase Hosting (current host) | None; run `firebase deploy --only hosting`, which reads the project from `.firebaserc` | `site`, set in `firebase.json` |
| Existing web hosting | None | Upload the contents of `site` to the public document root |
| GitHub Actions (this repository) | `python build.py` with Python 3.11 | `site`, deployed to Firebase Hosting |

`site\_headers` supplies the security headers on Cloudflare Workers, Cloudflare Pages and Netlify. `firebase.json` repeats them for Firebase Hosting and keeps `_headers` out of the upload; `validate.py` checks that the two stay identical. `firebase.json` also sends `Cache-Control: no-cache` on pages, so visitors see a new deployment on their next visit. Configure equivalent headers on other hosts. Scripts and styles are local assets; the supplied CSP does not allow inline scripts or styles. Use HTTPS. Cloudflare Pages, Netlify and Firebase Hosting serve `404.html` with HTTP status 404 automatically, and Cloudflare Workers does once `not_found_handling` is `404-page`; configure the same on other hosts.

On Windows, the Firebase Hosting emulator applies no header rules: its `glob-slash` dependency builds request paths with backslashes, so no rule matches. Check headers on the deployed site instead.

### Current deployment

The site is live at https://asdaria.web.app (also served at `asdaria.firebaseapp.com`) from Firebase project `asdaria` on the free Spark plan, and search engines may index it. The project belongs to the Google account that created it; add the company account as an Owner under **Project settings** > **Users and permissions**. The public source repository is https://github.com/ronaldndirangu/asdaria. No custom domain has been configured.

`SITE_URL` in `build.py` sets the public address. From it, the build gives every page except `404.html` a canonical link and `og:url`, and writes `sitemap.xml` and `robots.txt`. Every page shares `assets/share.jpg`, a 1200 by 630 crop of the bakery photograph, as its link-preview image. `validate.py` checks that the pages, sitemap and `robots.txt` agree. To help Google find the site sooner, add https://asdaria.web.app to Google Search Console and submit the sitemap.

### Automated deployment

`.github\workflows\site.yml` builds the site, runs `validate.py`, checks JavaScript syntax, and rejects stale rendered files on pull requests and pushes to `main`. After a merge to `main`, the workflow deploys only `site` to the existing Firebase Hosting project. Pull requests never receive Google Cloud credentials and never deploy. Deployment jobs run serially. A manual workflow run on `main` can retry a deployment.

Authentication uses GitHub's short-lived OpenID Connect identity and Google Cloud Workload Identity Federation. No service-account key or Firebase login token is stored in the repository. The repository's Actions variables are:

| Variable | Value |
| --- | --- |
| `GCP_WORKLOAD_IDENTITY_PROVIDER` | Full Google Cloud workload identity provider resource name |
| `GCP_DEPLOY_SERVICE_ACCOUNT` | Email address of the Firebase deployment service account |

The identity provider and service-account binding must restrict access to this repository's numeric ID, its owner's numeric ID, and the `refs/heads/main` ref. The deployment service account needs Firebase Hosting Admin and Service Usage Consumer on project `asdaria`; the GitHub identity needs Workload Identity User on that account. Changes to the workflow require the same protected pull request path as other files.

For an emergency manual deployment outside GitHub, install the Firebase CLI once with `npm install -g firebase-tools` and sign in with `firebase login`, then run from this folder:

```powershell
python build.py
python validate.py
firebase deploy --only hosting
```

### Other hosts

Cloudflare Workers (`asdaria.<account-subdomain>.workers.dev`) and Cloudflare Pages (`asdaria.pages.dev`) also serve the site with the same security headers from `site\_headers`, which marks `asdaria.pages.dev` as `noindex`; on Workers, change that rule's host to the assigned `workers.dev` address. A custom domain on Workers must use Cloudflare nameservers. Cloudflare drops `.html` from addresses (for example `/about`) and redirects the linked `.html` addresses there, so links keep working; use the extensionless form for canonical URLs on Cloudflare.

## Owner checklist

The site is public, so confirm these with the directors and correct anything through `build.py` or `content.json`.

1. Add the company Google account as an Owner of Firebase project `asdaria`.
2. The owner supplied `asdaria.ltd@gmail.com` as the work email; it is linked throughout the site. The previous example address and personal email are not published.
3. Confirm +254733954103 and the postal address.
4. Confirm the directors' biographies, qualifications and approval to publish their portraits.
5. Approve the project register, team biographies, photo and organisation-logo publishing rights, and attribution. Numeric details within individual descriptions come from the supplied site and remain subject to owner approval. Unsupported aggregate marketing metrics have been omitted.
6. Confirm the AFPQ assignment's partner attribution. It follows the original site's placement outside ASDARIA company contracts.
7. Review Firebase Hosting's logging and privacy practices, then update `privacy.html` through `build.py` if needed.
8. To move to a custom domain, register it in ASDARIA Ltd's name, connect it under **Hosting** > **Add custom domain** in the Firebase console, set `SITE_URL` in `build.py` to it, then rebuild and deploy. The canonical links tell search engines to move to the new address, and the `web.app` address keeps working.

## Contact behaviour

Telephone and email links open the visitor's calling or email application. The work email is `asdaria.ltd@gmail.com`. In the footer they appear as labelled icons; the Contact page shows the full number and email address so desktop visitors can read or copy them. The project brief form validates input and opens a pre-filled draft in the visitor's email app, with the text shown for copying if no email app opens. It does not send messages, store enquiries or report a fabricated submission success. Clipboard failures show a manual-copy alternative. Add a real submission backend only after choosing its provider and privacy requirements.

## Source handling

The truncated ZIP was recovered by local headers; only entries passing length and CRC checks were used. The damaged final logo was excluded. An accessible replacement Word document subsequently supplied 40 embedded images and the source captions. Its seven project photographs and two caption-identified director portraits are used in the revamped site. The original protected attachment was not decrypted or bypassed. Original materials, extracted source images and recovery scripts remain outside the public directory.

The refined site follows the Word document's eight service lines and retains all 56 experience entries. Company assignments, the directors' assignments through other organisations and the directors' research appear in separately labelled sections. The AFPQ study appears in the business feasibility and development category and is linked from both relevant services. Project descriptions contain no calendar dates or years.

The owner requested project photography and director portraits after providing the accessible Word copy. Photograph captions follow the document: coffee infrastructure assessment, a climate adaptation field visit, the food hub, bakery, poultry-house layout, greenhouse drying and capacity-building preparation. The gallery does not establish a contract attribution for every photograph, so a photograph alone is not used to identify a company commission. The experience register supplies the delivery context. The dryer is identified as a greenhouse dryer for red pepper, rather than a poultry or handling facility; it illustrates post-harvest technology on Services and is deliberately kept out of the Experience page. The Experience page uses only the coffee and Kalobeyei feature photographs; the climate field visit and capacity-building photographs remain in the Gallery. The separately supplied transparent ASDARIA badge remains unchanged.

The owner also requested restoration of the organisation showcase. About uses the 28 logos supplied in the accessible Word profile and follows its explicit grouping: CELIM under ASDARIA company engagements, and the remaining organisations under directors' experience outside the company. Logo backgrounds were made transparent locally without recolouring the artwork. The source supplies a Global Cold Chain Alliance logo for the WFLO / GCCF entry, and the USAID logo for USAID / DAI. These historical experience references do not assert current partnerships or endorsements. The homepage links directly to the section.

Published photographs are locally encoded as WebP, with smaller responsive versions for larger source images. Director portraits have locally removed backgrounds, consistent square framing and circular presentation. Gallery photographs open in a lightbox with previous and next controls, arrow-key navigation and an icon close button, and open directly as images when JavaScript is unavailable. Image dimensions, descriptive alternative text and lazy loading are included; the homepage lead image loads eagerly. The growth strategy remains future intent, without claiming new partnerships, investments or outcomes.

## Validation

```powershell
python build.py
python validate.py
node --check site\assets\main.js
```

`validate.py` checks local page links and fragments, asset references, page landmarks, project attribution, service associations, contact consistency, footer structure, homepage counts against the source data, the Services index, gallery, About and Experience structure, light-only branding and content constraints. Browser checks should also cover mobile navigation, homepage reveals (including reduced motion and no JavaScript), the Experience practice tabs (keyboard use, sticky switching, next-practice cards, the phone tab grid and hidden-until-found panels), service-to-project deep links, the Services index, contact details above the fold, the gallery grid and lightbox keyboard interaction, the email draft form, footer icon labels and light-only rendering under dark device preferences.

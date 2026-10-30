# External services and food data research

Checked 2026-10-30 using official public documentation. These are published terms, not authenticated account entitlements or tested API results. Prices are USD before tax; recheck before selection or spending. No account, key, subscription, API inference, deployment or storage resource was created. Recommendations below are project judgments, not provider guarantees.

## Food data

| Source | Access, cost and rights | Coverage and recommendation |
| --- | --- | --- |
| [USDA FoodData Central API guide](https://fdc.nal.usda.gov/api-guide/) | data.gov key required; default 1,000 requests/hour/IP. Data is public domain under CC0; reuse, caching and redistribution permitted; USDA requests source acknowledgment. No paid API subscription is specified in the guide. | Foundation, legacy, survey and branded data have differing completeness. Useful base ingredients and some prepared foods, but Indian household coverage is not guaranteed. Start with a curated subset, retain FDC IDs, dataset and nutrient methods; avoid live upstream dependency for every diary read. |
| [ICMR-NIN IFCT 2017](https://www.nin.res.in/ebooks/IFCT2017.pdf) | Public PDF access is not a product redistribution license. The copyright statement requires prior written permission to reproduce/store electronically for a product. No supported public API, quota or product-license price was verified. | Strong Indian ingredient relevance. Do not scrape, bundle or cache as product data until written permission covers intended use and distribution. Cite Longvah et al., 2017 when licensed. |
| [IFCT general information](https://nin.res.in/ebooks/IFCT2017_16122024.pdf) | Describes dataset, not an API grant. | 528 foods, over 150 measured parameters; predominantly raw foods except poultry/eggs. Household cooked dishes still need preparation/yield modeling. |

No third dataset is selected: two incompatible licenses would add avoidable complexity now. Open branded-food sources can be reconsidered for barcode coverage, with a separate rights review before import.

### Source selection gate (Stage 4)

Build a coverage matrix for every Indian food category in PRD F04, including raw/cooked and oil variants. Each publishable row needs external source/version, URL, retrieval date, license/permission evidence, preparation description, reference mass, nutrient units/method, missingness and serving evidence. Show gaps honestly; do not relabel an unmatched Western food as an authoritative Indian dish. Where licensed cooked-dish data is absent, curate a documented ingredient-and-yield calculation using legally reusable inputs, label its preparation assumptions, and retain provenance. This internal catalog preparation does not imply delivering the user recipe editor before Stage 8.

Reject invalid units/reference mass and quarantine conflicting records. Preserve missing nutrients as unknown; a label without fiber cannot support a fiber-complete day. Keep source-reported energy; document kJ conversion and carbohydrate basis as specified in Architecture. Source corrections create versions. Cache only under verified terms; do not commit restricted datasets or personal food records. Authoritative production nutrition values have not been imported in Stage 1.

## AI comparison (Stage 10 candidates)

| Criterion | xAI candidate | Alternative: Google Gemini |
| --- | --- | --- |
| Suitable model | `grok-4.7`, shown in official [image understanding examples](https://docs.x.ai/developers/model-capabilities/images/understanding) | `gemini-2.5-flash`, listed in official [pricing](https://ai.google.dev/gemini-api/docs/pricing) with text/image/video input; confirm availability again at implementation |
| Structure | [JSON-schema structured outputs](https://docs.x.ai/developers/model-capabilities/text/structured-outputs); still validate semantics | [JSON-schema structured outputs](https://ai.google.dev/gemini-api/docs/structured-output), including Pydantic integration |
| Image transport | Inline encoded image supported; project uses stripped JPEG/PNG under its stricter size cap | [Inline image input](https://ai.google.dev/gemini-api/docs/image-understanding) supported; avoid persistent Files API for transient recognition |
| Published standard token cost | [Pricing](https://docs.x.ai/developers/pricing): Grok 4.7 below 200k prompt tokens, $2/M input, $6/M output; long-context rates higher. Image analysis consumes billed input tokens; image generation pricing is irrelevant. No guaranteed free API inference assumed. | [Pricing](https://ai.google.dev/gemini-api/docs/pricing): 2.5 Flash $0.30/M text/image/video input and $2.50/M output including thinking; limited free tier exists, with different data handling. |
| Rate limits | [Team/model/tier limits](https://docs.x.ai/developers/rate-limits), RPS and TPM; 429 on exceedance. Verify actual account limits later. | [Project/model/tier limits](https://ai.google.dev/gemini-api/docs/rate-limits), RPM/TPM/RPD; consult active account limits later. |
| Privacy | [API security FAQ](https://docs.x.ai/developers/faq/security): no training without permission; default 30-day input/output audit retention. Team-level ZDR has feature tradeoffs and must be verified. | [Terms](https://ai.google.dev/gemini-api/terms): unpaid content can be used for improvement and human review; do not submit sensitive/personal data. Paid-service data is not used for improvement but limited safety retention still applies. Review regional/age/use restrictions. |
| Latency/reliability | No meal-recognition benchmark or account SLA verified | No meal-recognition benchmark or account SLA verified |
| Switching cost | Backend adapter maps to shared validated proposal schema | Same proposal schema; provider-specific image/schema/error mapping stays in adapter |

Provisional recommendation: retain xAI as the requested primary evaluation candidate and Gemini as a cost comparison; do not select a production provider yet. Use a consented Indian-meal evaluation set at Stage 10: single foods, thali/mixed dishes, hidden oil, ambiguous portions, poor lighting and no-food images. Measure food-match top-k, portion error where measured ground truth exists, correction time, schema validity, failure rate, p50/p95 latency and billed cost per successful confirmed meal. A model-generated confidence score is not calibrated certainty. No model performance claim has been validated.

Cost estimate uses actual billed input/image/output/thinking tokens and retries, rather than a fixed price per photograph. For illustration only, 2,000 input and 500 output tokens at the listed standard rates would be $0.007 for Grok 4.7 or $0.00185 for Gemini 2.5 Flash; actual image tokenization and reasoning can change these totals. Before activation, choose per-user request caps, output limits, application spend ceiling and provider budget controls; no automatic paid-provider failover. Explicitly review data-processing terms and retention before any real user photo is uploaded.

## Platform, builds, hosting and monitoring

| Service/tool | Verified terms and intended use |
| --- | --- |
| [Supabase pricing](https://supabase.com/pricing) | Free: 500 MB database, 50,000 MAU, 1 GB storage, 5 GB egress plus 5 GB cached egress, two active projects; pauses after one inactive week. Pro starts $25/month, additional projects from $10/month, with usage overages. Suitable for later development evaluation; not an unlimited production commitment. Storage is unnecessary for transient photos. |
| [Expo/EAS pricing](https://expo.dev/pricing) | Expo tooling can be used locally; EAS Free lists 15 Android + 15 iOS builds with low-priority queue. Starter $19/month plus usage with build credit. Recheck quota/billing period and queue expectations in account before building. No EAS account or quota verified. |
| [Expo project setup](https://docs.expo.dev/get-started/create-a-project/) | Windows PowerShell supported and Node LTS required. Current docs describe SDK 58 transition, with physical Expo Go using SDK 57. Stage 2 must recheck and explicitly pick a matching SDK, RN and React set rather than trust an unqualified latest command. |
| [Expo development environment](https://docs.expo.dev/get-started/set-up-your-environment/) | Expo Go can validate the first minimal screen; own development builds support custom native modules and are the production-oriented path. Local Android builds require compatible SDK/JDK; cloud EAS avoids local compilation but needs later authorized account/build setup. |
| [APK builds](https://docs.expo.dev/build-reference/apk/) | EAS defaults to AAB; internal/APK profiles generate directly installable APKs. A development APK and release-like APK need actual device testing later. No build ran in Stage 1. |
| [Render free hosting](https://render.com/docs/free) | Python web-service candidate for later previews. Free services spin down after 15 minutes idle; local filesystem is ephemeral; shared usage limits apply. Provider says free instances are unsuitable for production. Use local FastAPI first; production hosting cost remains unselected. |
| [Render pricing](https://render.com/pricing) | Dynamic pricing table was not extractable in this session, so no paid compute price is claimed. Re-evaluate region, instance, egress, uptime and cost before deployment. |
| [Sentry pricing](https://sentry.io/pricing/) | Retrieval failed with unsupported Markdown content type. Current quota/price unverified. Start with local/redacted structured logs; hosted error monitoring remains optional and unselected. Recheck retention, PII controls, quota and overages before installation. |

Stage 1 actual spend: no chargeable resources or requests initiated. Local tools are separate from limited free hosted tiers. Production budgets must include database/egress/backups, backend compute, email delivery, monitoring, build usage and optional AI. Image storage and downloads add cost only if an explicit saved-photo feature is approved. No store enrollment fees or release-market costs were verified; evaluate during release preparation.

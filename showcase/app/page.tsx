import { getShowcaseData } from "../lib/real-showcase-data";
import { ShowcasePageClient } from "./showcase-page-client";

export default async function Page() {
  const data = await getShowcaseData();
  return <ShowcasePageClient {...data} />;
}

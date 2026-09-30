import { useEffect, useState } from "react";

const BUILD_DAY = new Date(`${__BUILD_DAY__}T00:00:00Z`);

/**
 * Today, for anything a page shows by date: commencement badges, where "today"
 * falls on a timeline. The first render uses the day the site was built, so it
 * matches the prerendered HTML and hydration has nothing to correct; once
 * mounted it moves to the reader's day.
 */
export function useToday() {
  const [today, setToday] = useState(BUILD_DAY);
  useEffect(() => setToday(new Date()), []);
  return today;
}

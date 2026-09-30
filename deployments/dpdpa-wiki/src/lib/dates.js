/**
 * Date helpers for commencement. No imports, so the browser bundle, the
 * prerender and the Vite plugin that builds the course records share them.
 */

const MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];

/** "2027-05-13" → "13 May 2027". Done by hand so the output does not depend on the build machine's locale. */
export function formatDate(iso) {
  const m = /^(\d{4})-(\d{2})-(\d{2})/.exec(String(iso || ""));
  if (!m) return "";
  return `${Number(m[3])} ${MONTHS[Number(m[2]) - 1]} ${Number(m[1])}`;
}

/** True/false when the record carries a commencement date; null when the date is not known. */
export function isInForce(p, onDate = new Date()) {
  if (!p.in_force_from) return null;
  return new Date(`${p.in_force_from}T00:00:00Z`).getTime() <= onDate.getTime();
}

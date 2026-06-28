#src/data_acquisition/fetch_footballratings_playwright.py
import csv
import traceback
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

try:
    from .data_sources import RAW_DIR
except ImportError:
    from data_sources import RAW_DIR


def _extract_table(page):
    tables = page.query_selector_all("table")
    for table in tables:
        # try to read headers
        thead = table.query_selector_all("thead th")
        if thead:
            headers = [h.inner_text().strip().lower() for h in thead]
        else:
            first_row = table.query_selector("tr")
            if not first_row:
                continue
            headers = [c.inner_text().strip().lower() for c in first_row.query_selector_all("th, td")]

        # pick tables that look like rankings (contain 'elo' or 'team')
        if not any("elo" in h or "team" in h for h in headers):
            continue

        rows = []
        body_rows = table.query_selector_all("tbody tr") or table.query_selector_all("tr")[1:]
        for tr in body_rows:
            cells = [c.inner_text().strip() for c in tr.query_selector_all("th, td")]
            rows.append(cells)

        # locate indices
        team_idx = next((i for i, h in enumerate(headers) if "team" in h), 0)
        rank_idx = next((i for i, h in enumerate(headers) if "rank" in h), None)
        elo_idx = next((i for i, h in enumerate(headers) if "elo" in h), None)

        processed = []
        for cells in rows:
            team = cells[team_idx] if team_idx is not None and team_idx < len(cells) else ""
            rank = cells[rank_idx] if rank_idx is not None and rank_idx < len(cells) else ""
            elo = cells[elo_idx] if elo_idx is not None and elo_idx < len(cells) else ""
            processed.append({"team": team, "rank": rank, "elo": elo})

        if processed:
            return processed

    return []


def fetch_footballratings(output_path: Path = None, headless: bool = True):
    url = "https://www.football-rankings.info/footballratings.html"
    output = output_path or (RAW_DIR / "footballratings_elo.csv")
    output.parent.mkdir(parents=True, exist_ok=True)

    # Try sequence: given headless param, then retry non-headless with UA and save debug HTML
    attempts = []
    try:
        with sync_playwright() as pw:
            # first attempt: as requested
            browser = pw.chromium.launch(headless=headless)
            page = browser.new_page()
            try:
                page.goto(url, timeout=60000)
                page.wait_for_load_state("networkidle", timeout=60000)
                data = _extract_table(page)
            except Exception as e:
                data = []
                attempts.append((headless, str(e)))
            browser.close()

            # if first attempt failed, try visible browser with a common browser UA
            if not data:
                ua = (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
                )
                browser = pw.chromium.launch(headless=False)
                context = browser.new_context(user_agent=ua)
                page = context.new_page()
                try:
                    page.goto(url, timeout=60000)
                    page.wait_for_load_state("networkidle", timeout=60000)
                    time.sleep(1)
                    data = _extract_table(page)
                except Exception as e:
                    attempts.append((False, str(e)))
                    # save debug HTML
                    try:
                        html = page.content()
                        debug_path = RAW_DIR / "footballratings_page_debug.html"
                        debug_path.write_text(html, encoding="utf-8")
                        print(f"Saved debug HTML to {debug_path}")
                    except Exception:
                        pass
                finally:
                    browser.close()

        if not data:
            print("No table extracted from FootballRatings page.")
            for a in attempts:
                print("Attempt:", a)
            return False

        # write CSV
        with output.open("w", encoding="utf-8", newline="") as fp:
            writer = csv.DictWriter(fp, fieldnames=["team", "rank", "elo"])
            writer.writeheader()
            for row in data:
                writer.writerow({
                    "team": row.get("team", ""),
                    "rank": row.get("rank", ""),
                    "elo": row.get("elo", ""),
                })

        print(f"Wrote {len(data)} rows to {output}")
        return True

    except Exception:
        traceback.print_exc()
        return False


if __name__ == "__main__":
    ok = fetch_footballratings()
    if not ok:
        print("Failed to fetch FootballRatings via Playwright. Check network and Playwright installation.")

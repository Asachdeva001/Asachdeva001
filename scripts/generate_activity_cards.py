import json
import os
import subprocess
from datetime import datetime, timedelta, timezone

USERNAME = "Asachdeva001"
OUTPUT_DIR = "assets/activity"

def get_github_token():
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN") or os.environ.get("METRICS_TOKEN")
    if not token:
        try:
            res = subprocess.run(["gh", "auth", "token"], capture_output=True, text=True)
            if res.returncode == 0 and res.stdout.strip():
                token = res.stdout.strip()
        except Exception:
            pass
    if not token:
        raise RuntimeError("No GitHub API token found in environment (GH_TOKEN, GITHUB_TOKEN, or METRICS_TOKEN).")
    return token

def fetch_graphql_data(token):
    today = datetime.now(timezone.utc).date()
    start = today - timedelta(days=370)

    query = """
    query($login: String!, $from: DateTime!, $to: DateTime!) {
      user(login: $login) {
        name
        login
        repositories(first: 100, ownerAffiliations: [OWNER], isFork: false) {
          totalCount
          nodes {
            name
            stargazerCount
            languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
              edges {
                size
                node {
                  name
                  color
                }
              }
            }
          }
        }
        contributionsCollection(from: $from, to: $to) {
          totalCommitContributions
          totalPullRequestContributions
          totalIssueContributions
          totalRepositoryContributions
          totalRepositoriesWithContributedCommits
          totalRepositoriesWithContributedPullRequests
          contributionCalendar {
            totalContributions
            weeks {
              contributionDays {
                date
                contributionCount
              }
            }
          }
        }
      }
    }
    """

    variables = {
        "login": USERNAME,
        "from": f"{start}T00:00:00Z",
        "to": f"{today}T23:59:59Z"
    }

    payload = json.dumps({"query": query, "variables": variables})
    res = subprocess.run(
        [
            "curl", "-sS", "-X", "POST",
            "-H", f"Authorization: bearer {token}",
            "-H", "Content-Type: application/json",
            "-H", "X-GitHub-Api-Version: 2022-11-28",
            "https://api.github.com/graphql",
            "-d", payload
        ],
        capture_output=True,
        text=True
    )

    if res.returncode != 0:
        raise RuntimeError(f"GraphQL request failed: {res.stderr}")

    data = json.loads(res.stdout)
    if "errors" in data:
        raise RuntimeError(f"GraphQL returned errors: {json.dumps(data['errors'], indent=2)}")

    user = data.get("data", {}).get("user")
    if not user:
        raise RuntimeError(f"User data for '{USERNAME}' was not returned.")

    return user, today

def build_svg_wrapper(title_slug, content, aria_label, neon_color="#0ea5e9"):
    return f'''<svg viewBox="0 0 1200 340" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{aria_label}">
  <defs>
    <!-- Background Gradient -->
    <linearGradient id="bg-grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#020617"/>
      <stop offset="50%" stop-color="#090d1a"/>
      <stop offset="100%" stop-color="#020617"/>
    </linearGradient>

    <!-- Glowing Filters -->
    <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="8" result="blur" />
      <feMerge>
        <feMergeNode in="blur" />
        <feMergeNode in="SourceGraphic" />
      </feMerge>
    </filter>

    <filter id="neon-glow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="0" stdDeviation="6" flood-color="{neon_color}" flood-opacity="0.4"/>
    </filter>

    <filter id="card-shadow" x="-10%" y="-10%" width="120%" height="120%">
      <feDropShadow dx="0" dy="4" stdDeviation="8" flood-color="#000" flood-opacity="0.5"/>
    </filter>

    <filter id="gold-glow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="0" stdDeviation="5" flood-color="#facc15" flood-opacity="0.4"/>
    </filter>
    <filter id="cyan-glow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="0" stdDeviation="5" flood-color="#38bdf8" flood-opacity="0.4"/>
    </filter>
    <filter id="purple-glow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="0" stdDeviation="5" flood-color="#a855f7" flood-opacity="0.4"/>
    </filter>
    <filter id="emerald-glow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="0" stdDeviation="5" flood-color="#34d399" flood-opacity="0.4"/>
    </filter>
    <filter id="orange-glow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="0" stdDeviation="5" flood-color="#f97316" flood-opacity="0.4"/>
    </filter>
    <filter id="red-glow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="0" stdDeviation="5" flood-color="#ef4444" flood-opacity="0.4"/>
    </filter>
  </defs>

  <style>
    .terminal-title {{
      font-family: 'Consolas', 'Fira Code', 'Courier New', monospace;
      font-size: 13px;
      fill: #64748b;
      font-weight: 500;
    }}
    .prompt-text {{
      font-family: 'Consolas', 'Fira Code', 'Courier New', monospace;
      font-size: 16px;
      fill: #38bdf8;
      font-weight: 600;
    }}
    .status-text-green {{
      font-family: 'Consolas', 'Fira Code', 'Courier New', monospace;
      font-size: 13px;
      fill: #34d399;
    }}
    .metric-value {{
      font-family: 'Segoe UI', -apple-system, sans-serif;
      font-weight: 700;
      fill: #f0f6fc;
    }}
    .metric-label {{
      font-family: 'Segoe UI', -apple-system, sans-serif;
      font-size: 11px;
      font-weight: 700;
      fill: #94a3b8;
      letter-spacing: 0.8px;
    }}
    .metric-subtext {{
      font-family: 'Segoe UI', -apple-system, sans-serif;
      font-size: 11px;
      fill: #64748b;
    }}
    .grid-lines {{
      fill: none;
      stroke: #1e293b;
      stroke-width: 0.8;
      stroke-dasharray: 4 4;
      opacity: 0.3;
    }}
    .tile-bg {{
      fill: #090d16;
      fill-opacity: 0.85;
      stroke: #1e293b;
      stroke-width: 1.5;
    }}
  </style>

  <!-- Background Rect -->
  <rect width="1200" height="340" fill="url(#bg-grad)" />

  <!-- Ambient Grid Lines -->
  <g class="grid-lines">
    <path d="M 0,40 L 1200,40 M 0,80 L 1200,80 M 0,120 L 1200,120 M 0,160 L 1200,160 M 0,200 L 1200,200 M 0,240 L 1200,240 M 0,280 L 1200,280 M 0,320 L 1200,320" />
    <path d="M 100,0 L 100,340 M 200,0 L 200,340 M 300,0 L 300,340 M 400,0 L 400,340 M 500,0 L 500,340 M 600,0 L 600,340 M 700,0 L 700,340 M 800,0 L 800,340 M 900,0 L 900,340 M 1000,0 L 1000,340 M 1100,0 L 1100,340" />
  </g>

  <!-- Glowing Particles in Background -->
  <circle cx="120" cy="80" r="60" fill="#06b6d4" fill-opacity="0.07" filter="url(#glow)">
    <animate attributeName="cx" values="120;220;120" dur="15s" repeatCount="indefinite"/>
  </circle>
  <circle cx="1080" cy="260" r="70" fill="#a855f7" fill-opacity="0.06" filter="url(#glow)">
    <animate attributeName="cx" values="1080;980;1080" dur="18s" repeatCount="indefinite"/>
  </circle>

  <!-- Outer Glow Border -->
  <rect x="40" y="25" width="1120" height="290" rx="12" fill="none" stroke="{neon_color}" stroke-width="1.5" filter="url(#neon-glow)" opacity="0.35"/>

  <!-- Main Window Body -->
  <rect x="40" y="25" width="1120" height="290" rx="12" fill="#050814" fill-opacity="0.94" stroke="#1e293b" stroke-width="1.5" filter="url(#card-shadow)"/>

  <!-- Terminal Header -->
  <path d="M 40 37 A 12 12 0 0 1 52 25 L 1148 25 A 12 12 0 0 1 1160 37 L 1160 60 L 40 60 Z" fill="#0b0f19" stroke="#1e293b" stroke-width="0.5"/>
  
  <!-- Window Controls -->
  <circle cx="65" cy="42" r="6" fill="#ef4444" />
  <circle cx="85" cy="42" r="6" fill="#eab308" />
  <circle cx="105" cy="42" r="6" fill="#22c55e" />

  <!-- Terminal Title -->
  <text x="600" y="46" text-anchor="middle" class="terminal-title">aashish@sachdeva:~/{title_slug}</text>

  <!-- Card Content -->
  {content}

</svg>'''

def main():
    token = get_github_token()
    user, today = fetch_graphql_data(token)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 1. Stats Data
    repos = user["repositories"]["nodes"]
    total_stars = sum(r["stargazerCount"] for r in repos)
    contribs = user["contributionsCollection"]
    total_commits = contribs["totalCommitContributions"]
    total_prs = contribs["totalPullRequestContributions"]
    total_issues = contribs["totalIssueContributions"]
    contributed_repos = max(
        contribs["totalRepositoriesWithContributedCommits"],
        contribs["totalRepositoriesWithContributedPullRequests"]
    )

    stats_content = f'''
  <text x="75" y="95" class="prompt-text" filter="url(#glow)">> npx get-github-stats</text>

  <!-- Stat Tile 1: Stars -->
  <g>
    <rect x="75" y="115" width="194" height="145" rx="12" class="tile-bg" stroke="#facc15" filter="url(#gold-glow)"/>
    <circle cx="172" cy="150" r="16" fill="#facc15" fill-opacity="0.15"/>
    <polygon points="172,141 176,149 185,150 178,156 180,165 172,160 164,165 166,156 159,150 168,149" fill="#facc15"/>
    <text x="172" y="196" text-anchor="middle" class="metric-value" font-size="28">{total_stars}</text>
    <text x="172" y="218" text-anchor="middle" class="metric-label">STARS EARNED</text>
    <text x="172" y="236" text-anchor="middle" class="metric-subtext">Across repositories</text>
  </g>

  <!-- Stat Tile 2: Commits -->
  <g>
    <rect x="289" y="115" width="194" height="145" rx="12" class="tile-bg" stroke="#38bdf8" filter="url(#cyan-glow)"/>
    <circle cx="386" cy="150" r="16" fill="#38bdf8" fill-opacity="0.15"/>
    <circle cx="386" cy="150" r="6" fill="none" stroke="#38bdf8" stroke-width="2.5"/>
    <line x1="370" y1="150" x2="377" y2="150" stroke="#38bdf8" stroke-width="2.5" stroke-linecap="round"/>
    <line x1="395" y1="150" x2="402" y2="150" stroke="#38bdf8" stroke-width="2.5" stroke-linecap="round"/>
    <text x="386" y="196" text-anchor="middle" class="metric-value" font-size="28" fill="#38bdf8">{total_commits:,}</text>
    <text x="386" y="218" text-anchor="middle" class="metric-label">TOTAL COMMITS</text>
    <text x="386" y="236" text-anchor="middle" class="metric-subtext">Past 365 days</text>
  </g>

  <!-- Stat Tile 3: Pull Requests -->
  <g>
    <rect x="503" y="115" width="194" height="145" rx="12" class="tile-bg" stroke="#a855f7" filter="url(#purple-glow)"/>
    <circle cx="600" cy="150" r="16" fill="#a855f7" fill-opacity="0.15"/>
    <path d="M593 143 L593 157 M607 143 V150 A4 4 0 0 1 603 154 L593 154" fill="none" stroke="#a855f7" stroke-width="2" stroke-linecap="round"/>
    <circle cx="593" cy="143" r="2" fill="#a855f7"/>
    <circle cx="593" cy="157" r="2" fill="#a855f7"/>
    <circle cx="607" cy="143" r="2" fill="#a855f7"/>
    <text x="600" y="196" text-anchor="middle" class="metric-value" font-size="28" fill="#a855f7">{total_prs}</text>
    <text x="600" y="218" text-anchor="middle" class="metric-label">PULL REQUESTS</text>
    <text x="600" y="236" text-anchor="middle" class="metric-subtext">Merged &amp; opened</text>
  </g>

  <!-- Stat Tile 4: Issues -->
  <g>
    <rect x="717" y="115" width="194" height="145" rx="12" class="tile-bg" stroke="#ef4444" filter="url(#red-glow)"/>
    <circle cx="814" cy="150" r="16" fill="#ef4444" fill-opacity="0.15"/>
    <circle cx="814" cy="150" r="8" fill="none" stroke="#ef4444" stroke-width="2"/>
    <circle cx="814" cy="150" r="2.5" fill="#ef4444"/>
    <text x="814" y="196" text-anchor="middle" class="metric-value" font-size="28">{total_issues}</text>
    <text x="814" y="218" text-anchor="middle" class="metric-label">TOTAL ISSUES</text>
    <text x="814" y="236" text-anchor="middle" class="metric-subtext">Tracked &amp; reported</text>
  </g>

  <!-- Stat Tile 5: Contributed Repos -->
  <g>
    <rect x="931" y="115" width="194" height="145" rx="12" class="tile-bg" stroke="#34d399" filter="url(#emerald-glow)"/>
    <circle cx="1028" cy="150" r="16" fill="#34d399" fill-opacity="0.15"/>
    <path d="M1020 143 H1036 V157 H1020 Z" fill="none" stroke="#34d399" stroke-width="2"/>
    <path d="M1024 147 H1032 M1024 151 H1030" stroke="#34d399" stroke-width="1.5" stroke-linecap="round"/>
    <text x="1028" y="196" text-anchor="middle" class="metric-value" font-size="28" fill="#34d399">{contributed_repos}</text>
    <text x="1028" y="218" text-anchor="middle" class="metric-label">CONTRIBUTED TO</text>
    <text x="1028" y="236" text-anchor="middle" class="metric-subtext">Projects &amp; repos</text>
  </g>

  <!-- Footer Status -->
  <text x="75" y="292" class="status-text-green">> status: 100% synchronized with GitHub API</text>
'''

    svg_stats = build_svg_wrapper("github-stats", stats_content, "GitHub Statistics", neon_color="#0ea5e9")
    with open(os.path.join(OUTPUT_DIR, "github-stats.svg"), "w", encoding="utf-8") as f:
        f.write(svg_stats)

    # 2. Streak Data
    calendar = contribs["contributionCalendar"]
    weeks = calendar["weeks"]
    days = []
    for week in weeks:
        for day in week["contributionDays"]:
            days.append({"date": day["date"], "count": day["contributionCount"]})

    days.sort(key=lambda x: x["date"])
    day_map = {d["date"]: d["count"] for d in days}

    current_streak = 0
    cursor = today
    if day_map.get(str(cursor), 0) == 0:
        cursor -= timedelta(days=1)

    while day_map.get(str(cursor), 0) > 0:
        current_streak += 1
        cursor -= timedelta(days=1)

    longest_streak = 0
    running = 0
    for day in days:
        if day["count"] > 0:
            running += 1
            longest_streak = max(longest_streak, running)
        else:
            running = 0

    total_contributions = sum(d["count"] for d in days)

    streak_content = f'''
  <text x="75" y="95" class="prompt-text" filter="url(#glow)">> npx get-streak-status</text>

  <!-- Module 1: Current Streak -->
  <g>
    <rect x="75" y="115" width="330" height="145" rx="12" class="tile-bg" stroke="#f97316" filter="url(#orange-glow)"/>
    
    <!-- Flame Icon -->
    <g transform="translate(100, 140)">
      <circle cx="20" cy="20" r="20" fill="#f97316" fill-opacity="0.15"/>
      <path d="M20 8 C20 8 13 18 13 24 C13 28 16 31 20 31 C24 31 27 28 27 24 C27 18 20 8 20 8 Z" fill="#f97316"/>
      <path d="M20 18 C20 18 16 23 16 26 C16 28 18 29 20 29 C22 29 24 28 24 26 C24 23 20 18 20 18 Z" fill="#fbbf24"/>
    </g>

    <text x="155" y="152" class="metric-label">CURRENT STREAK</text>
    <text x="155" y="188" class="metric-value" font-size="32" fill="#f97316">{current_streak} <tspan font-size="20" fill="#94a3b8" font-weight="500">Days</tspan></text>
    <text x="155" y="212" class="metric-subtext">Active continuous contribution streak</text>
  </g>

  <!-- Module 2: Longest Streak -->
  <g>
    <rect x="435" y="115" width="330" height="145" rx="12" class="tile-bg" stroke="#facc15" filter="url(#gold-glow)"/>
    
    <!-- Trophy Icon -->
    <g transform="translate(460, 140)">
      <circle cx="20" cy="20" r="20" fill="#facc15" fill-opacity="0.15"/>
      <path d="M12 11 H28 V20 C28 24.4 24.4 28 20 28 C15.6 28 12 24.4 12 20 Z" fill="none" stroke="#facc15" stroke-width="2"/>
      <path d="M16 28 H24 V32 H16 Z M14 32 H26" stroke="#facc15" stroke-width="2" stroke-linecap="round"/>
      <path d="M8 13 C8 17 12 18 12 18 M32 13 C32 17 28 18 28 18" stroke="#facc15" stroke-width="2" stroke-linecap="round"/>
    </g>

    <text x="515" y="152" class="metric-label">LONGEST STREAK</text>
    <text x="515" y="188" class="metric-value" font-size="32" fill="#facc15">{longest_streak} <tspan font-size="20" fill="#94a3b8" font-weight="500">Days</tspan></text>
    <text x="515" y="212" class="metric-subtext">All-time record streak length</text>
  </g>

  <!-- Module 3: Total Contributions -->
  <g>
    <rect x="795" y="115" width="330" height="145" rx="12" class="tile-bg" stroke="#34d399" filter="url(#emerald-glow)"/>
    
    <!-- Activity Pulse Icon -->
    <g transform="translate(820, 140)">
      <circle cx="20" cy="20" r="20" fill="#34d399" fill-opacity="0.15"/>
      <path d="M8 20 H14 L18 10 L23 30 L27 16 L30 20 H32" fill="none" stroke="#34d399" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
    </g>

    <text x="875" y="152" class="metric-label">PAST 365 DAYS</text>
    <text x="875" y="188" class="metric-value" font-size="30" fill="#34d399">{total_contributions:,}</text>
    <text x="875" y="212" class="metric-subtext">Total contributions recorded</text>
  </g>

  <!-- Footer Status -->
  <text x="75" y="292" class="status-text-green">> streak status: Active &amp; consistent • Updated automatically every 6 hours</text>
'''

    svg_streak = build_svg_wrapper("streak-tracker", streak_content, "GitHub Streak Statistics", neon_color="#f97316")
    with open(os.path.join(OUTPUT_DIR, "streak.svg"), "w", encoding="utf-8") as f:
        f.write(svg_streak)

    # 3. Languages Data
    lang_map = {}
    for r in repos:
        for edge in r["languages"]["edges"]:
            lname = edge["node"]["name"]
            lcolor = edge["node"]["color"] or "#8b949e"
            size = edge["size"]
            if lname not in lang_map:
                lang_map[lname] = {"size": 0, "color": lcolor}
            lang_map[lname]["size"] += size

    total_lang_size = sum(l["size"] for l in lang_map.values())
    sorted_langs = sorted(lang_map.items(), key=lambda x: x[1]["size"], reverse=True)[:6]

    bar_x = 75
    bar_y = 120
    bar_w = 1050
    bar_h = 16

    segments_svg = ""
    current_x = bar_x

    for name, info in sorted_langs:
        pct = (info["size"] / total_lang_size * 100) if total_lang_size > 0 else 0
        seg_w = (pct / 100) * bar_w
        if seg_w > 0:
            segments_svg += f'<rect x="{current_x:.2f}" y="{bar_y}" width="{seg_w:.2f}" height="{bar_h}" fill="{info["color"]}"/>\n'
            current_x += seg_w

    badges_svg = ""
    col_widths = 330
    gap_x = 30
    start_x = 75

    for i, (name, info) in enumerate(sorted_langs[:6]):
        row = i // 3
        col = i % 3
        bx = start_x + col * (col_widths + gap_x)
        by = 155 + row * 58
        pct = (info["size"] / total_lang_size * 100) if total_lang_size > 0 else 0
        color = info["color"]

        badges_svg += f'''
    <g transform="translate({bx}, {by})">
      <rect x="0" y="0" width="{col_widths}" height="48" rx="8" class="tile-bg" stroke="{color}" stroke-opacity="0.6"/>
      <circle cx="20" cy="24" r="6" fill="{color}"/>
      <text x="35" y="29" font-family="'Segoe UI', sans-serif" font-size="14" font-weight="700" fill="#f0f6fc">{name}</text>
      <text x="{col_widths - 15}" y="29" text-anchor="end" font-family="'Segoe UI', sans-serif" font-size="14" font-weight="700" fill="{color}">{pct:.1f}%</text>
      <line x1="35" y1="36" x2="{35 + (col_widths - 50) * (pct/100):.1f}" y2="36" stroke="{color}" stroke-width="2" stroke-linecap="round"/>
    </g>
    '''

    langs_content = f'''
  <text x="75" y="95" class="prompt-text" filter="url(#glow)">> npx get-top-languages</text>

  <!-- Segmented Multi-Color Progress Bar -->
  <g>
    <rect x="{bar_x}" y="{bar_y}" width="{bar_w}" height="{bar_h}" rx="8" fill="#090d16" stroke="#1e293b" stroke-width="1.5"/>
    <clipPath id="bar-clip">
      <rect x="{bar_x}" y="{bar_y}" width="{bar_w}" height="{bar_h}" rx="8"/>
    </clipPath>
    <g clip-path="url(#bar-clip)">
      {segments_svg}
    </g>
  </g>

  <!-- Language Grid Cards -->
  {badges_svg}

  <!-- Footer Status -->
  <text x="75" y="292" class="status-text-green">> language breakdown: Analyzed across user repositories</text>
'''

    svg_langs = build_svg_wrapper("language-metrics", langs_content, "Top Languages Used", neon_color="#3178c6")
    with open(os.path.join(OUTPUT_DIR, "top-langs.svg"), "w", encoding="utf-8") as f:
        f.write(svg_langs)

    print("Activity cards updated successfully!")

if __name__ == "__main__":
    main()

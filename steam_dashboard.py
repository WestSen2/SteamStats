import pandas as pd
import streamlit as st

from SteamStat import (
    STEAM_ID,
    collect_stats,
    describe_status,
    describe_visibility,
    format_timestamp,
)

st.set_page_config(page_title="Steam Stats Viewer", layout="centered")
st.title("Steam Stats Viewer")
st.caption("Enter a Steam ID to pull the player summary, games, and friends list.")

with st.form("steam_id_form"):
    steam_id = st.text_input("Steam ID", value=STEAM_ID)
    submitted = st.form_submit_button("Fetch stats")

if submitted:
    steam_id = steam_id.strip()
    if not steam_id:
        st.warning("Please provide a Steam ID before fetching stats.")
    else:
        with st.spinner("Fetching stats..."):
            try:
                stats = collect_stats(steam_id)
            except Exception as exc:
                st.error(f"Unable to fetch stats: {exc}")
            else:
                player = stats["player"]
                player_raw = player.get("raw", {})
                status = describe_status(player["status"])

                st.subheader(player["name"])
                player_columns = st.columns([1, 3])
                with player_columns[1]:
                    st.markdown(
                        f"**Status:** {status}  \n"
                        f"**SteamID:** {player['steamid']}  \n"
                        f"**Profile:** [Link]({player['profile_url']})"
                    )
                avatar_url = player_raw.get("avatarfull")
                if avatar_url:
                    player_columns[0].image(avatar_url, width=120)

                player_details = [
                    ("Steam ID", player["steamid"]),
                    ("Status", status),
                    ("Real Name", player_raw.get("realname", "Not provided")),
                    (
                        "Visibility",
                        describe_visibility(player_raw.get("communityvisibilitystate")),
                    ),
                    ("Profile State", player_raw.get("profilestate", "Unknown")),
                    ("Primary Clan", player_raw.get("primaryclanid", "Unknown")),
                    (
                        "Account Created",
                        format_timestamp(player_raw.get("timecreated")),
                    ),
                    (
                        "Last Logoff",
                        format_timestamp(player_raw.get("lastlogoff")),
                    ),
                    ("Country", player_raw.get("loccountrycode", "Unknown")),
                    ("State Code", player_raw.get("locstatecode", "Unknown")),
                    ("City ID", player_raw.get("loccityid", "Unknown")),
                ]
                st.table(pd.DataFrame(player_details, columns=["Field", "Value"]))

                games = stats["games"]
                if games:
                    st.subheader("Owned Games")
                    total_hours = sum(game["hours"] for game in games)
                    average_hours = total_hours / len(games)
                    recently_played = sum(1 for game in games if game["two_weeks"] > 0)
                    game_metrics = st.columns(4)
                    game_metrics[0].metric("Total Games", len(games))
                    game_metrics[1].metric("Total Hours", f"{total_hours:.1f}h")
                    game_metrics[2].metric("Avg Hours / Game", f"{average_hours:.1f}h")
                    game_metrics[3].metric("Played in 2 Weeks", recently_played)

                    games_df = pd.DataFrame(
                        [
                            {
                                "Game": game["name"],
                                "AppID": game["appid"],
                                "Hours Played": game["hours"],
                                "2 Weeks": game["two_weeks"],
                                "Last Played": game["last_played"],
                                "Windows": game["windows_hours"],
                                "Mac": game["mac_hours"],
                                "Linux": game["linux_hours"],
                                "Has Stats": "Yes" if game["has_stats"] else "No",
                            }
                            for game in games
                        ]
                    )
                    st.dataframe(games_df, use_container_width=True)
                    with st.expander("Raw owned games payloads"):
                        st.json([game["raw"] for game in games])
                else:
                    st.info("No owned games data returned.")

                friends = stats["friends"]
                st.subheader(f"Friend List ({len(friends)})")
                online_count = sum(1 for friend in friends if friend["status"] != 0)
                friend_metrics = st.columns(3)
                friend_metrics[0].metric("Total Friends", len(friends))
                friend_metrics[1].metric("Online Now", online_count)
                friend_metrics[2].metric("Offline", len(friends) - online_count)

                if friends:
                    friend_rows = [
                        {
                            "Friend": friend["name"],
                            "SteamID": friend["steamid"],
                            "Status": describe_status(friend["status"]),
                            "Visibility": describe_visibility(
                                friend["raw"].get("communityvisibilitystate")
                            ),
                            "Last Logoff": format_timestamp(
                                friend["raw"].get("lastlogoff")
                            ),
                            "Country": friend["raw"].get("loccountrycode", "Unknown"),
                        }
                        for friend in friends
                    ]
                    st.dataframe(pd.DataFrame(friend_rows), use_container_width=True)
                    with st.expander("Raw friend summaries"):
                        st.json([friend["raw"] for friend in friends])
                else:
                    st.info("No friends were returned for this Steam ID.")

                with st.expander("Complete API payloads"):
                    st.json(
                        {
                            "player_summary": player_raw,
                            "owned_games": [game["raw"] for game in games] if games else [],
                            "friend_summaries": [friend["raw"] for friend in friends]
                            if friends
                            else [],
                        }
                    )

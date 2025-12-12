import pandas as pd
import streamlit as st

from SteamStat import STEAM_ID, collect_stats, describe_status

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
                st.subheader(player["name"])
                status = describe_status(player["status"])
                st.markdown(f"**Status:** {status}  \n**SteamID:** {player['steamid']}  \n**Profile:** [Link]({player['profile_url']})")

                games = stats["games"]
                if games:
                    st.subheader("Owned Games")
                    games_df = pd.DataFrame([
                        {
                            "Game": game["name"],
                            "Hours Played": game["hours"],
                            "2 Weeks": game["two_weeks"],
                            "Last Played": game["last_played"],
                        }
                        for game in games
                    ])
                    st.table(games_df.reset_index(drop=True))
                else:
                    st.info("No owned games data returned.")

                friends = stats["friends"]
                st.subheader(f"Friend List ({len(friends)})")
                if friends:
                    st.table([
                        {"Friend": friend["name"], "Status": describe_status(friend["status"]), "SteamID": friend["steamid"]}
                        for friend in friends
                    ])
                else:
                    st.info("No friends were returned for this Steam ID.")


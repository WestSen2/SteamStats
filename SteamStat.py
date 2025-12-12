import requests
from datetime import datetime
from prettytable import PrettyTable

# --- CONFIG ---
API_KEY = "1C1D19710437EE482A3513DAF7C125AF"

PERSONA_STATES = {
    0: "Offline",
    1: "Online",
    2: "Busy",
    3: "Away",
    4: "Snooze",
    5: "Looking to Trade",
    6: "Looking to Play",
}

COMMUNITY_VISIBILITY = {
    1: "Private",
    2: "Friends Only",
    3: "Friends of Friends",
    4: "Users Only",
    5: "Public",
}

STEAM_ID = "76561199077231505"  # numeric SteamID

# --- FUNCTIONS ---

# --- API HELPERS ---

def get_player_summary(steam_id):
    url = f"http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={API_KEY}&steamids={steam_id}"
    response = requests.get(url).json()
    player = response['response']['players'][0]
    return {
        "name": player['personaname'],
        "status": player['personastate'],
        "profile_url": player['profileurl'],
        "steamid": player['steamid'],
        "raw": player,
    }


def format_last_played(timestamp):
    if not timestamp:
        return "Never"
    return datetime.utcfromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M UTC")


def format_timestamp(timestamp):
    if not timestamp:
        return "Unknown"
    return datetime.utcfromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M UTC")


def get_owned_games(steam_id):
    url = (
        "http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/"
        f"?key={API_KEY}&steamid={steam_id}&include_appinfo=1&include_played_free_games=1&count=0"
    )
    response = requests.get(url).json()
    games = response.get('response', {}).get('games', [])
    return [
        {
            "name": game.get('name', 'Unknown'),
            "appid": game.get('appid'),
            "hours": round(game.get('playtime_forever', 0) / 60, 1),
            "two_weeks": round(game.get('playtime_2weeks', 0) / 60, 1),
            "last_played": format_last_played(game.get('rtime_last_played')),
            "windows_hours": round(game.get('playtime_windows_forever', 0) / 60, 1),
            "mac_hours": round(game.get('playtime_mac_forever', 0) / 60, 1),
            "linux_hours": round(game.get('playtime_linux_forever', 0) / 60, 1),
            "has_stats": game.get('has_community_visible_stats', False),
            "raw": game,
        }
        for game in games
    ]


def get_friends_list(steam_id):
    url = f"http://api.steampowered.com/ISteamUser/GetFriendList/v0001/?key={API_KEY}&steamid={steam_id}&relationship=friend"
    response = requests.get(url).json()
    friends = response.get('friendslist', {}).get('friends', [])
    return [friend['steamid'] for friend in friends]


def get_players_summaries(steam_ids):
    if not steam_ids:
        return []
    ids_param = ",".join(steam_ids)
    url = f"http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={API_KEY}&steamids={ids_param}"
    response = requests.get(url).json()
    players = response.get('response', {}).get('players', [])
    return [
        {
            "steamid": player['steamid'],
            "name": player['personaname'],
            "status": player['personastate'],
            "profile_url": player['profileurl'],
            "raw": player,
        }
        for player in players
    ]


def describe_status(persona_state):
    return PERSONA_STATES.get(persona_state, "Unknown")


def describe_visibility(state):
    return COMMUNITY_VISIBILITY.get(state, "Unknown")


def sort_games_by_hours(games):
    return sorted(games, key=lambda game: game['hours'], reverse=True)


def sort_friends(friend_summaries):
    def is_online(status):
        return status != 0

    return sorted(
        friend_summaries,
        key=lambda friend: (
            not is_online(friend['status']),
            friend['name'].lower()
        )
    )


def collect_stats(steam_id):
    player = get_player_summary(steam_id)
    games = sort_games_by_hours(get_owned_games(steam_id))
    friends = get_friends_list(steam_id)
    friend_summaries = sort_friends(get_players_summaries(friends)) if friends else []
    return {
        "player": player,
        "games": games,
        "friends": friend_summaries
    }

# --- MAIN ---
if __name__ == "__main__":
    stats = collect_stats(STEAM_ID)
    player = stats['player']
    print(f"Player: {player['name']}")
    print(f"Status: {describe_status(player['status'])}")
    print(f"Profile: {player['profile_url']}\n")

    games = stats['games']
    if not games:
        print("Owned Games & Hours Played: none found")
    else:
        table = PrettyTable(['Game', 'Hours Played', '2 Weeks', 'Last Played'])
        for game in games:
            table.add_row([
                game['name'],
                game['hours'],
                game['two_weeks'],
                game['last_played'],
            ])
        print("Owned Games & Hours Played:")
        print(table)

    friends = stats['friends']
    print(f"\nNumber of Friends: {len(friends)}")
    if friends:
        friend_table = PrettyTable(['Friend', 'Status', 'SteamID'])
        for friend in friends:
            friend_table.add_row([
                friend['name'],
                describe_status(friend['status']),
                friend['steamid']
            ])
        print("Friends List:")
        print(friend_table)
    else:
        print("Friends List: no friends found")

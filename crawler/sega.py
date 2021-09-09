"""
crawler.py

Crawler for the Rhythm Game
"""
import re
import requests
from .config import SEGA_USERNAME, SEGA_PASSWORD

def get_maimai_data(username, password, user_idx=0):
    """ (str, str, str) -> dict

    Crawl maimai data from the official website.
    Note: JP version

    >>> get_maimai_data("stypr", "password")
    """
    host = "https://maimaidx.jp/maimai-mobile"
    headers = {"User-Agent": "Mozilla/5.0"}
    result = {}
    r = requests.Session()

    # get token from login
    response = r.get(f"{host}/", headers=headers, verify=False)
    response_token = re.findall(
        '<input type="hidden" name="token" value="(.*)" />',
        response.text
    )
    if not response_token:
        return result
    response_token = response_token[0]
    data = {
        "segaId": username,
        "password": password,
        "save_cookie": "save_cookie",
        "token": response_token
    }
    response = r.post(f"{host}/submit/", data, headers=headers, verify=False)
    if response.url != f"{host}/aimeList/":
        return result
    response = r.get(f"{host}/aimeList/submit/?idx={user_idx}", verify=False)

    # parse user information from home
    if response.url != f"{host}/home/":
        return result
    user_extra = re.findall(
        f'<img src="(.+)" class="(.+)?h_35(.+)?"(.+)?>',
        response.text
    )
    user_extra = [i[0] for i in user_extra]
    user_title = re.findall(
        '<div class="trophy_block.+">\n.+\n.+<span>(.+)</span>',
        response.text,
    )
    user_nickname = re.findall(
        '<div class="name_block.+">(.+)</div>',
        response.text
    )
    user_rating = re.findall(
        '<div class="rating_block .+">(.+)</div>',
        response.text
    )

    result["info"] = {
        "title": user_title[0],
        "nickname": user_nickname[0].strip(),
        "current_rating": int(user_rating[0]),
        "extra": user_extra
    }

    # parse latest 10 playlogs
    result["log"] = []
    response = r.get(f"{host}/record/", verify=False)
    user_log = response.text.split('<div class="playlog_top_container">')[1:-1]
    for _log in user_log[:10]:
        _log_date = re.findall(
            '<span class="v_b">(.+)</span>',
            _log
        )
        _log_title = re.findall(
            '<div class="basic_block .+">(<img.+/>)?(.+)</div>',
            _log
        )
        _log_difficulty = re.findall(
            f'<img src="{host}/img/diff_(.+).png" class="playlog_diff .+"/>',
            _log
        )
        _log_score_sign = re.findall(
            f'<img src="{host}/img/playlog/(.+).png?.+" class="playlog_scorerank"/>',
            _log
        )
        _log_score = re.findall(
            '<div class="playlog_achievement_txt t_r">(.+)<span class=.+>(.+)</span>',
            _log,
        )
        _log_is_new_record = re.findall(
            f'{host}/img/playlog/newrecord.png',
            _log
        )
        # need to implement fc, etc.
        result["log"].append(
            {
                "date": _log_date[0].strip(),
                "title": _log_title[0][1].strip(),
                "difficulty": _log_difficulty[0].upper(),
                "score_sign": _log_score_sign[0],
                "is_new_record": bool(_log_is_new_record),
                "score": _log_score[0][0] + _log_score[0][1],
            }
        )

    return result


def get_chunithm_data(username, password, user_idx=0):
    """ (str, str, str) -> dict

    Crawl chunithm data from the official website.

    >>> get_chunithm_data("stypr", "password")
    """
    host = "https://chunithm-net.com/mobile"
    headers = {"User-Agent": "Mozilla/5.0"}
    result = {}
    r = requests.Session()

    # get token from login
    response = r.get(f"{host}/", headers=headers)
    response_token = re.findall(
        '<input type="hidden" name="token" value="(.*)" />',
        response.text
    )
    if not response_token:
        return result
    response_token = response_token[0]
    data = {
        "segaId": username,
        "password": password,
        "save_cookie": "save_cookie",
        "token": response_token
    }
    response = r.post(f"{host}/submit/", data, headers=headers)
    if response.url != f"{host}/aimeList/":
        return result
    response_token = re.findall(
        '<input type="hidden" name="token" value="(.*)" />',
        response.text
    )
    if not response_token:
        return result
    response_token = response_token[0]
    data = {
        "idx": user_idx,
        "token": response_token
    }
    response = r.post(f"{host}/aimeList/submit/", data)

    # parse user information from home
    if response.url != f"{host}/home/":
        return result
    user_team = re.findall(
        '<div class="player_team_name .+">(.+)</div>',
        response.text
    )
    user_title = re.findall(
        '<div class="player_honor_text"><span(.+)?>(.+)</span></div>',
        response.text,
    )
    user_nickname = re.findall(
        '<div class="player_name">\n.+\n(.+)\n.+</div>',
        response.text
    )
    user_level = re.findall(
        '<div class="player_lv"><span.+>.+</span>(.+)</div>',
        response.text
    )
    user_ratings = re.findall(
        (
            '<div class="player_rating">\n.+'
            + 'RATING : (.+) / '
            + '\(<span.+>.+</span> (.+)\)'
        ),
        response.text,
    )

    result["info"] = {
        "title": user_title[0][1],
        "nickname": user_nickname[0].strip(),
        "level": user_level[0],
        "current_rating": user_ratings[0][0],
        "max_rating": user_ratings[0][1],
        "team": user_team[0],
    }

    # parse latest 10 playlogs
    result["log"] = []
    response = r.get(f"{host}/record/playlog")
    user_log = response.text.split('<div class="frame02 w400">')[1:-1]
    for _log in user_log[:10]:
        _log_date = re.findall(
            '<div class="play_datalist_date">(.+)</div>',
            _log
        )
        _log_title = re.findall(
            '<div class="play_musicdata_title">(.+)</div>',
            _log
        )
        _log_difficulty = re.findall(
            f'<img src="{host}/images/icon_text_(.+).png">',
            _log
        )
        _log_score_sign = re.findall(
            f'<img src="{host}/images/icon_rank_(.+).png" />',
            _log
        ) # 1 = C, 10 = SSS
        _log_score = re.findall(
            '<div class="play_musicdata_score_text">Score：(.+)</div>',
            _log,
        )
        _log_extra = re.findall(
            '<img src="(.+.png)".+/>',
            _log.split('<div class="play_musicdata_icon clearfix">')[1]
        )
        _log_is_new_record = re.findall(
            f'{host}/images/icon_newrecord.jpg',
            _log
        )
        result["log"].append(
            {
                "date": _log_date[0].strip(),
                "title": _log_title[0].strip(),
                "difficulty": _log_difficulty[0].upper(),
                "score_sign": _log_score_sign[0],
                "is_new_record": bool(_log_is_new_record),
                "score": int(_log_score[0].strip().replace(",", "")),
                "extra": _log_extra,
            }
        )

    return result

def get_ongeki_data(username, password, user_idx=0):
    """ (str, str, str) -> dict

    Crawl ongeki data from the official website.

    >>> get_ongeki_data("stypr", "password")
    """
    host = "https://ongeki-net.com/ongeki-mobile"
    headers = {"User-Agent": "Mozilla/5.0"}
    result = {}
    r = requests.Session()

    # get token from login
    response = r.get(f"{host}/", headers=headers)
    response_token = re.findall(
        '<input type="hidden" name="token" value="(.*)" />',
        response.text
    )
    if not response_token:
        return result

    # authenticate and select user idx
    data = {
        "segaId": username,
        "password": password,
        "token": response_token
    }
    response = r.post(f"{host}/submit/", data, headers=headers)
    if response.url != f"{host}/aimeList/":
        return result
    response = r.get(f"{host}/aimeList/submit/?idx={user_idx}")

    # parse user information from Home
    if response.url != f"{host}/home/":
        return result
    user_title = re.findall(
        r"<div class=\"trophy_block .+\">\n.+<span>(.+)</span>\n.+</div>",
        response.text
    )
    user_nickname = re.findall(
        r"<div class=\"name_block\ .+\">\n.+<span>(.+)</span>\n.+</div>",
        response.text
    )
    user_level_reincarnation = re.findall(
        r"<div class=\"reincarnation_block\">\n.+<span>(.+)</span>\n.+</div>",
        response.text,
    )
    user_level = re.findall(
        r"<div class=\"lv_block\ .+\">\n.+<span>(.+)</span>\n.+</div>",
        response.text
    )
    user_ratings = re.findall(
        (
            '<div class="rating_field .+">\n.+'
            + '<span class=".+">(.+)</span>'
            + '<span class=".+">(.+)</span>'
        ),
        response.text,
    )
    user_bp = re.findall(
        r"<div class=\"battle_rank_block\">\n.+\n.+<div class=\".+\">(.+)</div>\n",
        response.text,
    )
    if user_level_reincarnation:
        user_level = user_level_reincarnation[0] + user_level[0]
    else:
        user_level = user_level[0]
    user_level = int(user_level.replace(",", ""))
    result["info"] = {
        "title": user_title[0],
        "nickname": user_nickname[0],
        "level": user_level,
        "current_rating": user_ratings[0][0],
        "max_rating": user_ratings[0][1],
        "battle_point": int(user_bp[0].replace(",", "")),
    }

    # parse latest 10 playlogs
    result["log"] = []
    response = r.get(f"{host}/record/playlog")
    user_log_raw = response.text.split('<div class="container3 t_l">')[1]
    user_log = user_log_raw.split('<div class="clearfix"></div>')[:-1]
    for _log in user_log[:10]:
        _log_date = re.findall(
            '<span class="f_r f_12 h_10">(.+)</span>',
            _log
        )
        _log_title = re.findall(
            '<div class="m_5 l_h_10 break">\n.+<img .+>(.+)\n.+</div>',
            _log
        )
        _log_difficulty = re.findall(
            f'<img src="{host}/img/diff_(.+).png" />',
            _log
        )
        _log_score_sign = re.findall(
            f'<img src="{host}/img/score_tr_(.+).png".+>',
            _log
        )
        _log_score = re.findall(
            '<td class="technical_score_block(.+)?">\n.+\n.+<div class=".+">(.+)</div>\n',
            _log,
        )
        _log_extra = re.findall(
            '<img src="(.+.png)".+/>',
            _log.split('div class="clearfix p_t_5 t_l f_0">')[1]
        )
        result["log"].append(
            {
                "date": _log_date[0].strip(),
                "title": _log_title[0].strip(),
                "difficulty": _log_difficulty[0].upper(),
                "score_sign": _log_score_sign[0].upper(),
                "is_new_record": bool(_log_score[0][0]),
                "score": int(_log_score[0][1].strip().replace(",", "")),
                "extra": _log_extra,
            }
        )

    return result

def collect_data():
    """ collect data """
    result = {}
    result['ongeki'] = get_ongeki_data(SEGA_USERNAME, SEGA_PASSWORD)
    result['chunithm'] = get_chunithm_data(SEGA_USERNAME, SEGA_PASSWORD)
    result['maimai'] = get_maimai_data(SEGA_USERNAME, SEGA_PASSWORD)
    return result

if __name__ == "__main__":
    assert SEGA_USERNAME and SEGA_PASSWORD
    print(get_ongeki_data(SEGA_USERNAME, SEGA_PASSWORD))
    print(get_chunithm_data(SEGA_USERNAME, SEGA_PASSWORD))
    print(get_maimai_data(SEGA_USERNAME, SEGA_PASSWORD))

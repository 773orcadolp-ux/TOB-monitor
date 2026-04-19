PE_FUND_ADDRESSES = [
    {"name": "KKR Japan",                    "address": "東京都千代田区大手町",    "prefecture": "東京都"},
    {"name": "Blackstone Japan",             "address": "東京都港区赤坂",          "prefecture": "東京都"},
    {"name": "Carlyle Japan",                "address": "東京都千代田区丸の内",    "prefecture": "東京都"},
    {"name": "Bain Capital Japan",           "address": "東京都港区赤坂",          "prefecture": "東京都"},
    {"name": "Apollo Global Japan",          "address": "東京都千代田区永田町",    "prefecture": "東京都"},
    {"name": "CVC Capital Japan",            "address": "東京都千代田区丸の内",    "prefecture": "東京都"},
    {"name": "MBK Partners Japan",           "address": "東京都千代田区大手町",    "prefecture": "東京都"},
    {"name": "Permira Japan",                "address": "東京都港区虎ノ門",        "prefecture": "東京都"},
    {"name": "EQT Japan",                    "address": "東京都千代田区丸の内",    "prefecture": "東京都"},
    {"name": "PAG",                          "address": "東京都港区赤坂",          "prefecture": "東京都"},
    {"name": "Warburg Pincus Japan",         "address": "東京都千代田区丸の内",    "prefecture": "東京都"},
    {"name": "TPG Japan",                    "address": "東京都港区六本木",        "prefecture": "東京都"},
    {"name": "Advent International Japan",   "address": "東京都千代田区紀尾井町",  "prefecture": "東京都"},
    {"name": "日本産業パートナーズ(JIP)",    "address": "東京都千代田区大手町",    "prefecture": "東京都"},
    {"name": "ユニゾン・キャピタル",         "address": "東京都港区赤坂",          "prefecture": "東京都"},
    {"name": "アドバンテッジパートナーズ",   "address": "東京都港区元赤坂",        "prefecture": "東京都"},
    {"name": "丸の内キャピタル",             "address": "東京都千代田区丸の内",    "prefecture": "東京都"},
    {"name": "インテグラル",                 "address": "東京都千代田区丸の内",    "prefecture": "東京都"},
    {"name": "ポラリス・キャピタル・グループ", "address": "東京都港区赤坂",        "prefecture": "東京都"},
    {"name": "グロービス・キャピタル",       "address": "東京都千代田区麹町",      "prefecture": "東京都"},
    {"name": "NSSK",                         "address": "東京都千代田区永田町",    "prefecture": "東京都"},
    {"name": "フェニックス・キャピタル",     "address": "東京都港区西新橋",        "prefecture": "東京都"},
]

LISTED_COMPANY_ADDRESSES = [
    {"name": "三菱商事",                     "address": "東京都千代田区丸の内",    "prefecture": "東京都"},
    {"name": "三井物産",                     "address": "東京都千代田区大手町",    "prefecture": "東京都"},
    {"name": "住友商事",                     "address": "東京都千代田区大手町",    "prefecture": "東京都"},
    {"name": "伊藤忠商事",                   "address": "東京都港区北青山",        "prefecture": "東京都"},
    {"name": "丸紅",                         "address": "東京都千代田区大手町",    "prefecture": "東京都"},
    {"name": "三菱UFJフィナンシャル・グループ", "address": "東京都千代田区丸の内", "prefecture": "東京都"},
    {"name": "三井住友フィナンシャルグループ", "address": "東京都千代田区丸の内",  "prefecture": "東京都"},
    {"name": "みずほフィナンシャルグループ", "address": "東京都千代田区大手町",    "prefecture": "東京都"},
    {"name": "ソニーグループ",               "address": "東京都港区港南",          "prefecture": "東京都"},
    {"name": "トヨタ自動車",                 "address": "愛知県豊田市トヨタ町",    "prefecture": "愛知県"},
    {"name": "NTT",                          "address": "東京都千代田区大手町",    "prefecture": "東京都"},
    {"name": "キーエンス",                   "address": "大阪府大阪市東淀川区",    "prefecture": "大阪府"},
    {"name": "ソフトバンクグループ",         "address": "東京都港区東新橋",        "prefecture": "東京都"},
    {"name": "ファーストリテイリング",       "address": "山口県山口市佐山",        "prefecture": "山口県"},
    {"name": "富士フイルムホールディングス", "address": "東京都港区赤坂",          "prefecture": "東京都"},
    {"name": "日立製作所",                   "address": "東京都千代田区丸の内",    "prefecture": "東京都"},
    {"name": "パナソニックホールディングス", "address": "大阪府門真市大字門真",    "prefecture": "大阪府"},
    {"name": "セブン＆アイ・ホールディングス", "address": "東京都千代田区二番町",  "prefecture": "東京都"},
    {"name": "KDDI",                         "address": "東京都千代田区飯田橋",    "prefecture": "東京都"},
    {"name": "日本電産",                     "address": "京都府京都市南区久世殿城町", "prefecture": "京都府"},
]

ALL_WATCH_ADDRESSES = PE_FUND_ADDRESSES + LISTED_COMPANY_ADDRESSES

def get_all_addresses():
    return ALL_WATCH_ADDRESSES

def get_address_strings():
    return [entry["address"] for entry in ALL_WATCH_ADDRESSES]

def find_matching_entity(address: str):
    for entry in ALL_WATCH_ADDRESSES:
        if entry["address"] in address or address in entry["address"]:
            return entry["name"]
    return "不明"

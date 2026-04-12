# PEファンド・上場会社の住所マスタ

PE_FUND_ADDRESSES = [
    {"name": "KKR Japan", "address": "東京都千代田区大手町一丁目9番2号", "prefecture": "東京都"},
    {"name": "Blackstone Japan", "address": "東京都港区赤坂一丁目12番32号", "prefecture": "東京都"},
    {"name": "Carlyle Japan", "address": "東京都千代田区丸の内二丁目4番1号", "prefecture": "東京都"},
    {"name": "Bain Capital Japan", "address": "東京都港区赤坂二丁目17番7号", "prefecture": "東京都"},
    {"name": "Apollo Global Japan", "address": "東京都千代田区永田町二丁目11番1号", "prefecture": "東京都"},
    {"name": "CVC Capital Japan", "address": "東京都千代田区丸の内一丁目8番3号", "prefecture": "東京都"},
    {"name": "MBK Partners Japan", "address": "東京都千代田区大手町二丁目2番1号", "prefecture": "東京都"},
    {"name": "Permira Japan", "address": "東京都港区虎ノ門四丁目1番28号", "prefecture": "東京都"},
    {"name": "EQT Japan", "address": "東京都千代田区丸の内三丁目2番3号", "prefecture": "東京都"},
    {"name": "PAG", "address": "東京都港区赤坂九丁目7番1号", "prefecture": "東京都"},
    {"name": "Warburg Pincus Japan", "address": "東京都千代田区丸の内二丁目4番1号", "prefecture": "東京都"},
    {"name": "TPG Japan", "address": "東京都港区六本木六丁目10番1号", "prefecture": "東京都"},
    {"name": "Advent International Japan", "address": "東京都千代田区紀尾井町4番1号", "prefecture": "東京都"},
    {"name": "日本産業パートナーズ(JIP)", "address": "東京都千代田区大手町一丁目2番1号", "prefecture": "東京都"},
    {"name": "ユニゾン・キャピタル", "address": "東京都港区赤坂二丁目14番27号", "prefecture": "東京都"},
    {"name": "アドバンテッジパートナーズ", "address": "東京都港区元赤坂一丁目2番7号", "prefecture": "東京都"},
    {"name": "丸の内キャピタル", "address": "東京都千代田区丸の内二丁目4番1号", "prefecture": "東京都"},
    {"name": "インテグラル", "address": "東京都千代田区丸の内一丁目8番2号", "prefecture": "東京都"},
    {"name": "ポラリス・キャピタル・グループ", "address": "東京都港区赤坂一丁目12番32号", "prefecture": "東京都"},
    {"name": "グロービス・キャピタル", "address": "東京都千代田区麹町三丁目2番4号", "prefecture": "東京都"},
    {"name": "NSSK", "address": "東京都千代田区永田町二丁目11番1号", "prefecture": "東京都"},
    {"name": "フェニックス・キャピタル", "address": "東京都港区西新橋一丁目6番15号", "prefecture": "東京都"},
]

LISTED_COMPANY_ADDRESSES = [
    {"name": "三菱商事", "address": "東京都千代田区丸の内三丁目2番3号", "prefecture": "東京都"},
    {"name": "三井物産", "address": "東京都千代田区大手町一丁目2番1号", "prefecture": "東京都"},
    {"name": "住友商事", "address": "東京都千代田区大手町二丁目3番2号", "prefecture": "東京都"},
    {"name": "伊藤忠商事", "address": "東京都港区北青山二丁目5番1号", "prefecture": "東京都"},
    {"name": "丸紅", "address": "東京都千代田区大手町一丁目4番2号", "prefecture": "東京都"},
    {"name": "三菱UFJフィナンシャル・グループ", "address": "東京都千代田区丸の内二丁目7番1号", "prefecture": "東京都"},
    {"name": "三井住友フィナンシャルグループ", "address": "東京都千代田区丸の内一丁目1番2号", "prefecture": "東京都"},
    {"name": "みずほフィナンシャルグループ", "address": "東京都千代田区大手町一丁目5番5号", "prefecture": "東京都"},
    {"name": "ソニーグループ", "address": "東京都港区港南一丁目7番1号", "prefecture": "東京都"},
    {"name": "トヨタ自動車", "address": "愛知県豊田市トヨタ町一番地", "prefecture": "愛知県"},
    {"name": "NTT", "address": "東京都千代田区大手町二丁目3番1号", "prefecture": "東京都"},
    {"name": "キーエンス", "address": "大阪府大阪市東淀川区東中島一丁目3番14号", "prefecture": "大阪府"},
    {"name": "ソフトバンクグループ", "address": "東京都港区東新橋一丁目9番1号", "prefecture": "東京都"},
    {"name": "ファーストリテイリング", "address": "山口県山口市佐山717番地1", "prefecture": "山口県"},
    {"name": "富士フイルムホールディングス", "address": "東京都港区赤坂九丁目7番3号", "prefecture": "東京都"},
    {"name": "日立製作所", "address": "東京都千代田区丸の内一丁目6番6号", "prefecture": "東京都"},
    {"name": "パナソニックホールディングス", "address": "大阪府門真市大字門真1006番地", "prefecture": "大阪府"},
    {"name": "セブン＆アイ・ホールディングス", "address": "東京都千代田区二番町8番地8", "prefecture": "東京都"},
    {"name": "KDDI", "address": "東京都千代田区飯田橋三丁目10番10号", "prefecture": "東京都"},
    {"name": "日本電産", "address": "京都府京都市南区久世殿城町338番地", "prefecture": "京都府"},
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

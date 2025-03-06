# -*- coding: utf-8 -*-
from typing import Optional

from sudachipy import tokenizer
from sudachipy import dictionary
from sudachipy import config
from sudachipy import MorphemeList, Morpheme
import braille_rules
import pybraille

mode = tokenizer.Tokenizer.SplitMode.B
tokenizer_obj = dictionary.Dictionary().create(mode)
braille_rules.load_b_railleRules()

def score_part_of_speech(morpheme: Morpheme, pos) -> Optional[int]:
    for index, m_pos in enumerate(morpheme.part_of_speech()):
        if (index <= len(morpheme.part_of_speech())
        and (m_pos == pos or pos == '*')):
            return index
    return None

def search_braille_rules(morpheme: Morpheme) -> Optional[int]:
    max_score = -1
    rule_index = -1
    for index, rule in enumerate(braille_rules.rules.rule):
        score = score_part_of_speech(morpheme, rule.current_pos.name)
        if score is not None and score > max_score:
            max_score = score
            rule_index = index
    if rule_index < 0:
        return None
    else:
        return rule_index

def search_next_rule(morpheme: Morpheme, rule) -> Optional[int]:
    max_score = -1
    next_index = -1
    for index, n_rule in enumerate(rule.next_pos):
        score = score_part_of_speech(morpheme, n_rule.name)
        if score is not None and score > max_score:
            max_score = score
            next_index = index
    if next_index < 0:
        return None
    return next_index

def is_space_required(current_morpheme: Morpheme, next_morpheme: Morpheme) -> bool:
    space_flag: bool = True # 与えられた2つの品詞間にスペースが必要かどうか
    rule_index = search_braille_rules(current_morpheme)
    if rule_index is not None:
        rule = braille_rules.rules.rule[rule_index]
        rule_index = search_next_rule(next_morpheme, rule)
        if rule_index is not None:
            space_flag = rule.next_pos[rule_index].before_space
        else:
            space_flag = False
    else:
        space_flag = False
    # print(space_flag)
    return space_flag

def is_kana_conversion_required(morphe: Morpheme):
    if (morphe.part_of_speech()[0] == "補助記号"
        or morphe.part_of_speech()[0] == "空白"
        or morphe.part_of_speech()[1] == "数詞"
        or morphe.reading_form() == morphe.surface()
    ):
        return False
    return True

def convert_prolonged_sound_mark(morpheme):
    # 動詞以外の長音記号を変換する
    ret = list(morpheme.reading_form())
    if morpheme.part_of_speech()[0] != "動詞":
        for index in range(len(ret)):
            if index == 0:
                continue
            if ret[index] == "ウ":
                ret[index] = 'ー'
    return "".join(ret)

def convert_to_kana(src_string: str):
    kanaString: str = ""
    tokenized_list = tokenizer_obj.tokenize(src_string)
    for m_index, m in enumerate(tokenized_list):
        if m.part_of_speech()[0] == "助詞":
            # 助詞は、点字のルールで置換する
            if m.reading_form() == "ハ":
                kanaString += "ワ"
            elif m.reading_form() == "ヘ":
                kanaString += "エ"
            else:
                kanaString += m.reading_form()
        elif is_kana_conversion_required(m) == False:
            # その品詞は、そのまま表記を追加する
            kanaString += m.surface()
        else:
            # それ以外の品詞は、長音処理を行って読みを追加する
            kanaString += convert_prolonged_sound_mark(m)
        # この品詞のルールを、ルールリストに基づいて処理する
        if m_index < len(tokenized_list) - 1:
            if is_space_required(m, tokenized_list[m_index + 1]):
                kanaString += " "
    return kanaString

if __name__ == '__main__':
    src = "ソフトウェア"
    print(src)
    print(convert_to_kana(src))

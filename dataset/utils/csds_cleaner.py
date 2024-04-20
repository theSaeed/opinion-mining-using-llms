import re
import sys
import nltk
from nltk.tokenize import word_tokenize

nltk.download('punkt')

import json
# from json2csds.json2csds import JSON2CSDS
from json2csds import JSON2CSDS

from nltk.tokenize.treebank import TreebankWordDetokenizer

detokenizer = TreebankWordDetokenizer()

cache_clean_tokenizations_dict = {}
cache_tokenizations_dict = {}

global_dict_sentence_mismatches = {}
global_not_founds = {}
global_word_tokenization_mismatch = {}

def alert_wrong_anno(anno, doc_id, error=None):
    """
    It is used for alerting wrong annotation(s).
    :param anno: The annotation that error(s) were happening in its process.
    :param error: The error(s) that happened.
    """

    if str(error) != str("'text'"):
        print('===================\nWrong Clean!!')
        print(anno)
        print('Error details: (doc_id: ', doc_id, ')')
        print(error)
        print(f'Type of error: {error.__class__.__name__}')
        print('===================')


def white_in_warning(text):
    return f'\033[00m{text}\033[93m'


def white_in_error(text):
    return f'\033[00m{text}\033[91m'



def clean_item(txt):
    re_pattern = '[a-zA-Z0-9 _=+/\"\'\-]'

    txt = re.sub('\n', '  ', txt)
    txt = re.sub('<UH>', 'UUHH', txt)
    txt = re.sub('<' + re_pattern + '*>', '', txt)
    txt = re.sub(re_pattern + '+>', '', txt)
    txt = re.sub('--', ' -- ', txt)
    txt = re.sub('  ', ' ', txt)

    if txt == 'U.S' or txt == 'U. S.' or txt == 'U. S':
        txt = 'U.S.'

    # Handle ``s and ''s and `s
    start_quotation_marks_indices = []
    end_quotation_marks_indices = []
    quotation_marks_indices = []

    for i in range(len(txt) - 1):
        if txt[i:i + 2] == '``':  # or ord(txt[i]) == 39:
            start_quotation_marks_indices.append(i)
    for i in range(len(start_quotation_marks_indices)):
        txt = txt[0: start_quotation_marks_indices[i]] + '"' + txt[start_quotation_marks_indices[i] + 2:]
        if i+1 < len(start_quotation_marks_indices):
            start_quotation_marks_indices[i+1] -= 1

    for i in range(len(txt) - 1):
        if txt[i:i + 2] == "''":  # or ord(txt[i]) == 39:
            end_quotation_marks_indices.append(i)
    for i in range(len(end_quotation_marks_indices)):
        txt = txt[0: end_quotation_marks_indices[i]] + '"' + txt[end_quotation_marks_indices[i] + 2:]
        if i+1 < len(end_quotation_marks_indices):
            end_quotation_marks_indices[i+1] -= 1

    for i in range(len(txt)):
        if txt[i:i + 1] == '`':
            quotation_marks_indices.append(i)
    for i in range(len(quotation_marks_indices)):
        txt = txt[0: quotation_marks_indices[i]] + '\'' + txt[quotation_marks_indices[i] + 1:]

    return txt


def back_to_clean(lst):
    txt = detokenizer.detokenize(lst)
    txt = re.sub(' \.', '.', txt)
    txt = re.sub('\' ', '\'', txt)
    txt = re.sub('\" ', '"', txt)
    txt = re.sub('\. \"', '."', txt)
    txt = re.sub('\. \'', '.\'', txt)
    return txt


def cache_clean_tokenizations(text):
    if text not in cache_clean_tokenizations_dict:
        text2 = text + ' .'
        tokens = word_tokenize(clean_item(text2))
        tokens = list(map(clean_item, tokens))[0: -1]
        cache_clean_tokenizations_dict[text] = tokens
    return cache_clean_tokenizations_dict[text]


def cache_tokenizations(text):
    if text not in cache_clean_tokenizations_dict:
        text2 = text + ' .'
        tokens = word_tokenize(text2)[0:-1]
        cache_tokenizations_dict[text] = tokens
    return cache_tokenizations_dict[text]

def clean_plus_end(inp, end, start):
    if inp != []:
        final_input = inp.copy()
        j = 0
        length = len(inp)-1
        specific_symbols = ['"', '\'']

        if end == 1:
            length = len(inp)-2

        for i in range(length):
            if inp[i+1] == '.' and (inp[i])[0].isupper():
                final_input[j] += '.'
                final_input.pop(j+1)
            else:
                j += 1

        if end == 1:
            if final_input[-1] in specific_symbols:
                ind = -2
                if len(final_input) >= 2:
                    if final_input[-2] in specific_symbols:
                        ind = -3
                if len(final_input) >= abs(ind):
                    if final_input[ind].endswith('.') and len(final_input[ind])>1:
                        final_input[ind] = (final_input[ind])[0:-1]
                        final_input.insert(ind+1, '.')
            else:
                if final_input[-1].endswith('.') and len(final_input[-1])>1:
                    final_input[-1] = (final_input[-1])[0:-1]
                    final_input.append('.')

        if start == 1:
            for item_s in specific_symbols:
                if final_input[0].startswith(item_s) and len(final_input[0])>1:
                    if final_input[0][1].isupper() or len(final_input[0])>3:
                        final_input.insert(1, (final_input[0])[1:])
                        final_input[0] = item_s

        i = 0
        while(True):
            if i < len(final_input):
                if final_input[i] == 'U.S..':
                    final_input[i] = 'U.S.'

                if final_input[i].startswith('\'') and len(final_input[i]) > 1:
                    if final_input[i][1].isupper() or len(final_input[i]) > 3:
                        final_input.insert(i + 1, (final_input[i])[1:])
                        final_input[i] = '\''

                if i < len(final_input) - 1:
                    if final_input[i] == 'U.' and (final_input[i + 1] == 'S.' or final_input[i + 1] == 'S'):
                        final_input[i] = 'U.S.'
                        final_input.pop(i + 1)

                i += 1
            else:
                break


        return final_input
    else:
        return inp

def clean_plus_plus(tokens1, tokens2, tokens3, all_tokens):
    if all_tokens != []:
        i = 0
        # print(all_tokens)
        while(True):
            if i < len(all_tokens):
                if all_tokens[i].endswith('.'):
                    if tokens1 != []:
                        if tokens1[-1] == all_tokens[i][0:-1]:
                            all_tokens[i] = all_tokens[i][0:-1]
                            all_tokens.insert(i + 1, '.')

                    if tokens2 != []:
                        if tokens2[-1] == all_tokens[i][0:-1]:
                            all_tokens[i] = all_tokens[i][0:-1]
                            all_tokens.insert(i + 1, '.')

                    if tokens3 != []:
                        if tokens3[-1] == all_tokens[i][0:-1]:
                            all_tokens[i] = all_tokens[i][0:-1]
                            all_tokens.insert(i + 1, '.')
                i += 1
            else:
                break

        # print(all_tokens)

    return all_tokens

def clean_plus(text_tokens1, text_tokens2, text_tokens3, all_text_tokens):
    tokens1, tokens2, tokens3, all_tokens = text_tokens1, text_tokens2, text_tokens3, all_text_tokens

    # if all_text_tokens[len(text_tokens1): len(text_tokens1) + len(text_tokens2)] != text_tokens2:
    all_tokens = clean_plus_end(all_text_tokens, 1, 1)

    if text_tokens3 == []:
        #end = 2, all
        if text_tokens1 == []:
            # start = 2, all
            tokens2 = clean_plus_end(text_tokens2, 1, 1)
        else:
            # start = 1, all
            tokens1 = clean_plus_end(text_tokens1, 0, 1)
            tokens2 = clean_plus_end(text_tokens2, 1, 0)
    else:
        #end = 3, all
        tokens3 = clean_plus_end(text_tokens3, 1, 0)
        if text_tokens1 == []:
            # start = 2, all
            tokens2 = clean_plus_end(text_tokens2, 0, 1)
        else:
            # start = 1, all
            tokens1 = clean_plus_end(text_tokens1, 0, 1)
            tokens2 = clean_plus_end(text_tokens2, 0, 0)

    return tokens1, tokens2, tokens3, all_tokens


def char_to_word(item_id="", text="", head="", start=0, end=0, clean=False, verbose=False, remove=True):
    global global_word_tokenization_mismatch
    text1 = text[0: start]
    text2 = text[start: end]
    text3 = text[end:]

    if clean:
        text_tokens1 = cache_clean_tokenizations(text1)
        text_tokens2 = cache_clean_tokenizations(text2)
        text_tokens3 = cache_clean_tokenizations(text3)
        all_text_tokens = cache_clean_tokenizations(text)
        text_tokens1, text_tokens2, text_tokens3, all_text_tokens = clean_plus(text_tokens1, text_tokens2, text_tokens3, all_text_tokens)
        all_text_tokens = clean_plus_plus(text_tokens1, text_tokens2, text_tokens3, all_text_tokens)
    else:
        text_tokens1 = cache_tokenizations(text1)
        text_tokens2 = cache_tokenizations(text2)
        text_tokens3 = cache_tokenizations(text3)
        all_text_tokens = cache_tokenizations(text)

    if verbose and all_text_tokens[len(text_tokens1): len(text_tokens1) + len(text_tokens2)] != text_tokens2:
        if item_id in global_word_tokenization_mismatch:
            global_word_tokenization_mismatch[item_id + '(text, head, w_text, w_head)'].append([text, text2, all_text_tokens, text_tokens2])
        else:
            global_word_tokenization_mismatch[item_id + '(text, head, w_text, w_head)'] = [text, text2, all_text_tokens, text_tokens2]
        # print(
        #     f"\033[93m <Warning word tokenization mismatch id=<{white_in_warning(item_id)}>: \n\t head=<{white_in_warning(repr(text2))}> \n\t text=<{white_in_warning(repr(text))}> \n\t w_head={white_in_warning(text_tokens2)} \n\t w_text={white_in_warning(all_text_tokens)} \n /> \033[00m")

    # returns start index, list of tokens and the length of the tokens after the first index which should be considered
    if not remove:
        return {
            'w_head_span': (len(text_tokens1), len(text_tokens1) + len(text_tokens2)),
            'w_text': all_text_tokens,
            'w_head': text_tokens2,
            'clean_text': back_to_clean(all_text_tokens),
            'clean_head': back_to_clean(text_tokens2)
        }
    else:
        return {
            'w_head_span': (len(text_tokens1), len(text_tokens1) + len(text_tokens2)),
            'w_head': text_tokens2,
            'clean_head': back_to_clean(text_tokens2)
        }


def find_info(ids, data_subset, clean=False, add_attitude_attributes=False, parent_id='',
              verbose=False, data_targets={}, parent_text=''):
    global global_dict_sentence_mismatches
    global global_not_founds
    word_based_info = {}
    word_based_info_list = []
    if ids is None:
        return word_based_info_list
    for item_id in ids:
        if type(data_subset) is dict:
            if item_id in data_subset:
                item = data_subset[
                    item_id]  # dictionary: char based for sentence, word_based for sentence array, aspect, polarity, intensity, type
                if verbose and parent_text != '' and item['text'] != '' and parent_text != \
                        item['text']:
                    key_pch = 'parent:' + parent_id + 'child:' + item_id
                    if key_pch in global_dict_sentence_mismatches:
                        global_dict_sentence_mismatches[key_pch].append([parent_text, item['text']])
                    else:
                        global_dict_sentence_mismatches[key_pch] = [parent_text, item['text']]
                    # print(
                    #     f'\033[91m <Error sentence mismatch parent_id=<{white_in_error(parent_id)}> & child_id=<{white_in_error(item_id)}>: \n\t parent_text=\t{white_in_error(parent_text)} \n\t child_text=\t{white_in_error(item["text"])} \n /> \033[00m')
                else:
                    word_based_info = char_to_word(
                        item_id=item_id, text=item['text'], head=item['head'], start=item['head_start'],
                        end=item['head_end'], clean=clean, verbose=verbose
                    )
                    if add_attitude_attributes:
                        word_based_info.update({
                            'annotation_type': item['annotation_type'],
                            'polarity': item['polarity'],
                            'intensity': item['intensity'],
                            'target': find_info(item['target_link'], data_targets, clean
                                                , parent_id=item_id, verbose=False, parent_text = item['text'])
                        })
            elif verbose:
                if 'other' in global_not_founds:
                    global_not_founds['other'].append([item_id])
                else:
                    global_not_founds['other'] = [item_id]
                # print(f"\033[93m <Warning id=<{white_in_warning(item_id)}> couldn't be found./> \033[00m\033[00m")
        else:
            for item in data_subset:
                if item_id == item['unique_id']:
                    if verbose and parent_text != '' and item['text'] != '' and parent_text != \
                            item['text']:
                        flag = False
                        key_pch = 'parent:' + parent_id + 'child:' + item_id
                        if key_pch in global_dict_sentence_mismatches:
                            global_dict_sentence_mismatches[key_pch].append([parent_text, item['text']])
                        else:
                            global_dict_sentence_mismatches[key_pch] = [parent_text, item['text']]
                        # print(
                        # f'\033[91m <Error sentence mismatch parent_id=<{white_in_error(parent_id)}> & child_id=<{white_in_error(item_id)}>: \n\t parent_text=\t{white_in_error(parent_text)} \n\t child_text=\t{white_in_error(item["text"])} \n /> \033[00m')
                    else:
                        word_based_info = char_to_word(
                            item_id=item_id, text=item['text'], head=item['head'], start=item['head_start'],
                            end=item['head_end'], clean=clean, verbose=verbose
                        )
                        if add_attitude_attributes:
                            word_based_info.update({
                                'annotation_type': item['annotation_type'],
                                'polarity': item['polarity'],
                                'intensity': item['intensity'],
                                'target': find_info(item['target_link'], data_targets, clean,
                                                     parent_id=item_id, verbose=False, parent_text = item['text'])
                            })

        word_based_info_list.append(word_based_info)

    return word_based_info_list


def find_agent(ids, data_subset, parent, clean=False, parent_id='', agents_in_sentences={}, verbose=False):
    global global_dict_sentence_mismatches
    global global_not_founds
    word_based_info = {}
    word_based_info_list = []
    parent_text = parent['text']

    if ids is None:
        return word_based_info_list

    for item_id in ids:
        if item_id in data_subset:
            item = data_subset[item_id]  # dictionary: char based for sentence, word_based for sentence array, aspect, polarity, intensity, type

            if item_id.endswith('agent-w') or item_id.endswith('agent-implicit') or item['sentence_id'] == parent['sentence_id']:
                if verbose and parent_text != '' and item['text'] != '' and parent_text != \
                        item['text']:
                    key_pch = 'parent:' + parent_id + 'child:' + item_id
                    if key_pch in global_dict_sentence_mismatches:
                        global_dict_sentence_mismatches[key_pch].append([parent_text, item['text']])
                    else:
                        global_dict_sentence_mismatches[key_pch] = [parent_text, item['text']]
                    # print(
                    #     f'\033[91m <Error sentence mismatch parent_id=<{white_in_error(parent_id)}> & child_id=<{white_in_error(item_id)}>: \n\t parent_text=\t{white_in_error(parent_text)} \n\t child_text=\t{white_in_error(item["text"])} \n /> \033[00m')
                else:
                    word_based_info = char_to_word(
                        item_id=item_id, text=item['text'], head=item['head'], start=item['head_start'],
                        end=item['head_end'], clean=clean, verbose=verbose
                    )

            else:
                agent_found = False
                if parent['sentence_id'] in agents_in_sentences:
                    agents_in_sentence = agents_in_sentences[parent['sentence_id']]
                    for agent_id, agent in agents_in_sentence.items():
                        if len(agent['nested_source']) > 0 and agent['nested_source'][-1] == item_id:
                            word_based_info = char_to_word(
                                item_id=agent_id, text=agent['text'], head=agent['head'], start=agent['head_start'],
                                end=agent['head_end'], clean=clean, verbose=verbose
                            )
                            agent_found = True
                            break
                if not agent_found and verbose:
                    if 'agent (parent_id & child_id)' in global_not_founds:
                        global_not_founds['agent (parent_id & child_id)'].append([parent_id, item_id])
                    else:
                        global_not_founds['agent (parent_id & child_id)'] = [parent_id, item_id]
                    # print(f'\033[91m <Error agent not found (2 Hands) parent_id=<{white_in_error(parent_id)}> & child_id=<{white_in_error(item_id)}> & sentence-id=<{white_in_error(parent["sentence_id"])}>: \n\t parent_text=\t\t{white_in_error(parent_text)} \n\t supposed_text=\t{white_in_error(repr(item["text"]))} \n\t supposed_child_head=\t{white_in_error(repr(item["head"]))} \n /> \033[00m')
        elif verbose:
            if 'other' in global_not_founds:
                global_not_founds['other'].append([item_id])
            else:
                global_not_founds['other'] = [item_id]
            # print(f"\033[93m <Warning id=<{white_in_warning(item_id)}> couldn't be found./> \033[00m\033[00m")

        word_based_info_list.append(word_based_info)

    return word_based_info_list


def preprocess_agents_in_sentences(data_subset):
    agents_in_sentences = {}
    for agent_id, agent in data_subset.items():
        if agent['sentence_id'] not in agents_in_sentences:
            agents_in_sentences[agent['sentence_id']] = {agent_id: agent}
        else:
            agents_in_sentences[agent['sentence_id']][agent_id] = agent
    return agents_in_sentences


def tokenize_and_extract_info(data_address, save_address, clean=False, verbose=False, activate_progressbar=True):
    global global_dict_sentence_mismatches
    global global_not_founds
    global global_word_tokenization_mismatch

    # data_keys = ['csds_objects', 'agent_objects', 'target_objects']
    obj = JSON2CSDS("MPQA2.0", data_address, mpqa_version=2)
    # Gather the JSON file from MPQA.
    mpqa_json = obj.produce_json_file()
    data = obj.doc2csds(mpqa_json, json_output=True)

    agents_in_sentences = preprocess_agents_in_sentences(data['agent_objects'])

    # csds_objects
    n = len(data['csds_objects'])
    progressbar = -1
    for k in range(n):
        item = data['csds_objects'][k]

        word_based_info = char_to_word(
            text=item['text'], head=item['head'], start=item['head_start'], end=item['head_end'], clean=clean, remove=False
        )
        item.update(word_based_info)

        item_id = item['unique_id']
        item['target'] = find_info(item['target_link'], data['target_objects'], clean,
                                   parent_id=item_id, verbose=verbose, parent_text = item['text'])
        item['nested_source'] = find_agent(item['nested_source_link'], data['agent_objects'], item, clean,
                                           parent_id=item_id,
                                           agents_in_sentences=agents_in_sentences, verbose=verbose)
        item['attitude'] = find_info(item['attitude_link'], data['csds_objects'], clean, add_attitude_attributes=True,
                                     parent_id=item_id, verbose=verbose,
                                     data_targets=data['target_objects'], parent_text = item['text'])

        data['csds_objects'][k] = item

        if activate_progressbar and progressbar < k // (n // 100):
            progressbar = k // (n // 100)
            print(f'{progressbar}% completed (csds_objects)')

    # target_objects
    n = len(data['target_objects'])
    progressbar = -1
    j = 0
    for k in data['target_objects']:
        item = data['target_objects'][k]

        word_based_info = char_to_word(
            text=item['text'], head=item['head'], start=item['head_start'], end=item['head_end'], clean=clean, remove=False
        )
        item.update(word_based_info)

        data['target_objects'][k] = item

        if activate_progressbar and progressbar < j // (n // 100):
            progressbar = j // (n // 100)
            print(f'{progressbar}% completed (target_objects)')
        j += 1

    # agent_objects
    n = len(data['agent_objects'])
    progressbar = -1
    j = 0
    for k in data['agent_objects']:
        item = data['agent_objects'][k]

        word_based_info = char_to_word(
            text=item['text'], head=item['head'], start=item['head_start'], end=item['head_end'], clean=clean, remove=False
        )
        item.update(word_based_info)

        item_id = item['unique_id']
        item['nested_source_info'] = find_agent(item['nested_source'], data['agent_objects'], item, clean,
                                           parent_id=item_id,
                                           agents_in_sentences=agents_in_sentences, verbose=verbose)

        data['agent_objects'][k] = item

        if activate_progressbar and progressbar < j // (n // 100):
            progressbar = j // (n // 100)
            print(f'{progressbar}% completed (agent_objects)')
        j += 1

    with open(save_address, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    if verbose:
        global_dict = {
         'sentence_mismatch' : global_dict_sentence_mismatches,
         'not_found' : global_not_founds,
         'word_tokenization_mismatch' : global_word_tokenization_mismatch,
        }
        with open('problems.json', 'w', encoding='utf-8') as f:
            json.dump(global_dict, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    print(sys.argv[1])
    tokenize_and_extract_info(
        data_address=sys.argv[1]+'database.mpqa.2.0.cleaned',
        save_address='MPQA2.0_cleaned.json',
        clean=True,
        verbose=False
    )

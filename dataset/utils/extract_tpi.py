import os
import csv
import json
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--input-format',  '-i')
parser.add_argument('--output-format', '-o')
args = parser.parse_args()

INPUT_FORMAT = args.input_format
OUTPUT_FORMAT = args.output_format

# Doclists
ULA_SUBSET_DOCS = ['ula/119CWL041', 'ula/RindnerBonnie', 'ula/HistoryGreek', 'ula/Article247_3500', 'ula/NapierDianne', 'ula/sw2071-UTF16-ms98-a-trans', 'ula/118CWL050', 'ula/114CUL059', 'ula/110CYL067', 'ula/PolkMaria', 'ula/116CUL034', 'ula/115CVL037', 'ula/118CWL049', 'ula/Article247_66', 'ula/110CYL068', 'ula/113CWL017', 'ula/112C-L015', 'ula/115CVL036', 'ula/115CVL035', 'ula/Article247_328', 'ula/114CUL060', 'ula/112C-L012', 'ula/118CWL048', 'ula/ReidSandra', 'ula/112C-L016', 'ula/HistoryJerusalem', 'ula/110CYL070', 'ula/sw2014-UTF16-ms98-a-trans', 'ula/112C-L014', 'ula/117CWL008', 'ula/sw2078-UTF16-ms98-a-trans', 'ula/110CYL071', 'ula/114CUL057', 'ula/116CUL032', 'ula/110CYL069', 'ula/117CWL009', 'ula/110CYL072', 'ula/chapter-10', 'ula/116CUL033', 'ula/ch5', 'ula/sw2015-ms98-a-trans', 'ula/113CWL018', 'ula/110CYL200', 'ula/Article247_327', 'ula/114CUL058', 'ula/112C-L013', 'ula/Article247_500', 'ula/Article247_400']
ULA_LU_SUBSET_DOCS = ['ula/A1.E2-NEW', 'ula/wsj_1640.mrg-NEW', 'ula/AFGP-2002-600045-Trans', 'ula/20000410_nyt-NEW', 'ula/20000415_apw_eng-NEW', 'ula/AFGP-2002-602187-Trans', 'ula/20000815_AFP_ARB.0084.IBM-HA-NEW', 'ula/CNN_AARONBROWN_ENG_20051101_215800.partial-NEW', 'ula/20000424_nyt-NEW', 'ula/20000419_apw_eng-NEW', 'ula/20000416_xin_eng-NEW', 'ula/enron-thread-159550', 'ula/wsj_2465', 'ula/AFGP-2002-600002-Trans', 'ula/ENRON-pearson-email-25jul02', 'ula/im_401b_e73i32c22_031705-2', 'ula/A1.E1-NEW', 'ula/CNN_ENG_20030614_173123.4-NEW-1', 'ula/20000420_xin_eng-NEW', 'ula/IZ-060316-01-Trans-1', 'ula/sw2025-ms98-a-trans.ascii-1-NEW', 'ula/SNO-525', 'ula/AFGP-2002-600175-Trans', 'ula/602CZL285-1']
XBANK_DOCS = ['xbank/wsj_0904', 'xbank/wsj_0760', 'xbank/wsj_0713', 'xbank/wsj_0709', 'xbank/wsj_0706', 'xbank/wsj_0662', 'xbank/wsj_0558', 'xbank/wsj_0555', 'xbank/wsj_0551', 'xbank/wsj_0542', 'xbank/wsj_0541', 'xbank/wsj_0332', 'xbank/wsj_0292', 'xbank/wsj_0189', 'xbank/wsj_0316', 'xbank/wsj_0175', 'xbank/wsj_0321', 'xbank/wsj_0176', 'xbank/wsj_0173', 'xbank/wsj_0026', 'xbank/wsj_0324', 'xbank/wsj_0187', 'xbank/wsj_0356', 'xbank/wsj_0325', 'xbank/wsj_0340', 'xbank/wsj_0679', 'xbank/wsj_0695', 'xbank/wsj_0661', 'xbank/wsj_0570', 'xbank/wsj_0557', 'xbank/wsj_0751', 'xbank/wsj_0805', 'xbank/wsj_0762', 'xbank/wsj_0736', 'xbank/wsj_0806', 'xbank/wsj_1040', 'xbank/wsj_1039', 'xbank/wsj_1042', 'xbank/wsj_0568', 'xbank/wsj_0778', 'xbank/wsj_0160', 'xbank/wsj_0136', 'xbank/wsj_0135', 'xbank/wsj_0127', 'xbank/wsj_0122', 'xbank/wsj_0032', 'xbank/wsj_0150', 'xbank/wsj_0165', 'xbank/wsj_0157', 'xbank/wsj_0151', 'xbank/wsj_0685', 'xbank/wsj_0168', 'xbank/wsj_0167', 'xbank/wsj_0161', 'xbank/wsj_0152', 'xbank/wsj_0073', 'xbank/wsj_0068', 'xbank/wsj_0171', 'xbank/wsj_0144', 'xbank/wsj_0991', 'xbank/wsj_0923', 'xbank/wsj_0907', 'xbank/wsj_0811', 'xbank/wsj_0667', 'xbank/wsj_0534', 'xbank/wsj_0924', 'xbank/wsj_0815', 'xbank/wsj_1038', 'xbank/wsj_1035', 'xbank/wsj_1033', 'xbank/wsj_0527', 'xbank/wsj_0928', 'xbank/wsj_0973', 'xbank/wsj_0950', 'xbank/wsj_0927', 'xbank/wsj_0376', 'xbank/wsj_0660', 'xbank/wsj_0650', 'xbank/wsj_0266', 'xbank/wsj_0006', 'xbank/wsj_0768', 'xbank/wsj_1073', 'xbank/wsj_0816', 'xbank/wsj_0610', 'xbank/wsj_0583']
IGNORED_DOCS = ULA_SUBSET_DOCS + ULA_LU_SUBSET_DOCS + XBANK_DOCS
INPUT_FORMATS = {
    'T|A|S': ["T:A|S", "T:S|A", "T|A|S", "T|S|A", "A|S|T", "S|A|T", "T:T|A:A|S:S", "T:T|S:S|A:A", "A:A|S:S|T:T", "S:S|A:A|T:T", "T=T|A=A|S=S", "T=T|S=S|A=A", "A=A|S=S|T=T", "S=S|A=A|T=T"],
    'A|S': ["A|S", "S|A", "A:A|S:S", "A=A|S=S", "S:S|A:A", "S=S|A=A"],
    'S': ["S"],
    'A': ["A"],
}
OUTPUT_FORMATS = {
    't': ['t', 't(ordered)'],
    'p': ['p'],
    'i': ['i'],
    't|p|i:': ['t|p|i', 't|p|I:i', 't|P:p|i', 't|P:p|I:i', 'T:t|p|i', 'T:t|p|I:i', 'T:t|P:p|i', 'T:t|P:p|I:i'],
    't,p,i:': ['t,p,i', 't,p,I:i', 't,P:p,i', 't,P:p,I:i', 'T:t,p,i', 'T:t,p,I:i', 'T:t,P:p,i', 'T:t,P:p,I:i'],
    't|p|i=': ['t|p|i', 't|p|I=i', 't|P=p|i', 't|P=p|I=i', 'T=t|p|i', 'T=t|p|I=i', 'T=t|P=p|i', 'T=t|P=p|I=i'],
    't,p,i=': ['t,p,i', 't,p,I=i', 't,P=p,i', 't,P=p,I=i', 'T=t,p,i', 'T=t,p,I=i', 'T=t,P=p,i', 'T=t,P=p,I=i'],
}

#@title Parameters
REMOVE_PIPES_FROM_INPUT = False #@param {type: 'boolean'}
TEXT_KEY = 'clean_text' #@param ["text", "clean_text", "w_text"]
HEAD_KEY = 'clean_head' #@param ["head", "clean_head", "w_head"]
ADD_TASK_PREFIX = False #@param {type: 'boolean'}
CUSTOM_PREFIX = '' #@param {type: 'string'}

# Classes
TYPE_CLASSES = ['agreement', 'arguing', 'intention', 'sentiment']
POLARITY_CLASSES = ['negative', 'neutral', 'positive']
INTENSITY_CLASSES = ['low', 'low-medium', 'medium', 'medium-high', 'high', 'high-extreme', 'extreme']
POLARITY_DICT = {'negative': [1, 0, 0], 'neutral': [0, 1, 0], 'positive': [0, 0, 1]}
INTENSITY_DICT = {'low': [1, 0, 0], 'low-medium': [1, 1, 0], 'medium': [0, 1, 0], 'medium-high': [0, 1, 1], 'high': [0, 0, 1], 'high-extreme': [0, 0, 1], 'extreme': [0, 0, 1]}
NUM_TYPE_CLASSES = len(TYPE_CLASSES)
NUM_POLARITY_CLASSES = len(POLARITY_CLASSES)
NUM_INTENSITY_CLASSES = 3

# Create a map for class ids and class names
type_classname2classindex = {
    'agreement':               0,
    'arguing':                 1,
    'expressive_subjectivity': 2,
    'intention':               3,
    'sentiment':               4
}
type_classname2classid = {
    'agreement':               'agreement',
    'arguing':                 'arguing',
    'expressive_subjectivity': 'expressive',
    'intention':               'intention',
    'sentiment':               'sentiment'
}
type_classid2classname = {v:k for k, v in type_classname2classid.items()}
type_classid2classindex = {type_classname2classid[k]:v for k, v in type_classname2classindex.items()}

polarity_classname2classindex = {
    'negative': 0,
    'neutral':  1,
    'positive': 2,
}
polarity_classname2classid = {
    'negative': 'negative',
    'neutral':  'neutral',
    'positive': 'positive'
}
polarity_classid2classname = {v:k for k, v in polarity_classname2classid.items()}
polarity_classid2classindex = {polarity_classname2classid[k]:v for k, v in polarity_classname2classindex.items()}

intensity_classname2classindex = {
    'low':    0,
    'medium': 1,
    'high':   2,
}
intensity_classname2classid = {
    'low': 'low',
    'low-medium': 'low medium',
    'medium': 'medium',
    'medium-high': 'medium high',
    'high': 'high',
    'high-extreme': 'high',
    'extreme': 'high'
}
intensity_classid2classname = {v:k for k, v in intensity_classname2classid.items()}
intensity_classid2classindex = {intensity_classname2classid[k]:v for k, v in intensity_classname2classindex.items()}


# Keep the objects with the specified ids
def filter_csds_objects_all(csds_objects, train_ids, val_ids, test_ids):
    train_ids_set = set(train_ids)
    val_ids_set = set(val_ids)
    test_ids_set = set(test_ids)
    
    train_objects, val_objects, test_objects = [], [], []

    for csds_object in csds_objects:
        if csds_object['unique_id'] in val_ids_set:
            val_objects.append(csds_object)
        elif csds_object['unique_id'] in test_ids_set:
            test_objects.append(csds_object)
        elif csds_object['unique_id'] in train_ids_set:
            train_objects.append(csds_object)

    return train_objects, val_objects, test_objects


def generate_text_cognitive_state(output_format, annotype_id, polarity_id, intensity_id):
    output = ''

    inner_seperator = ''
    if ':' in output_format:
        inner_seperator = ' : '
    elif '=' in output_format:
        inner_seperator = ' = '

    outer_seperator = ''
    if '|' in output_format:
        outer_seperator = ' | '
    elif ',' in output_format:
        outer_seperator = ' , '

    if 'T' in output_format:
        output += 'type' + inner_seperator
    output += annotype_id + outer_seperator

    if 'P' in output_format:
        output += 'polarity' + inner_seperator
    output += polarity_id + outer_seperator

    if 'I' in output_format:
        output += 'intensity' + inner_seperator
    output += intensity_id

    return output


# Preparing inputs and targets
def prepare_inputs_and_targets(csds_objects):

    input_output_dict = {}
    n_samples = 0

    for csds_object in csds_objects:
        doc_id = csds_object['doc_id']
        unique_id = csds_object['unique_id']
        text = csds_object[TEXT_KEY]
        head = csds_object[HEAD_KEY]
        annotype  = csds_object['annotation_type']
        polarity  = csds_object['polarity']
        intensity = csds_object['intensity']

        if   INPUT_FORMAT in INPUT_FORMATS['T|A|S']:
            key = (annotype, head, text)
        elif INPUT_FORMAT in INPUT_FORMATS['A|S']:
            key = (head, text)
        elif INPUT_FORMAT in INPUT_FORMATS['A']:
            key = (head,)
        elif INPUT_FORMAT in INPUT_FORMATS['S']:
            key = (text,)
        else:
            print("INPUT FORMAT NOT SUPPORTED IN prepare_inputs_and_targets")

        if annotype in TYPE_CLASSES and polarity in POLARITY_CLASSES and intensity in INTENSITY_CLASSES \
            and doc_id not in IGNORED_DOCS:
            
            annotype_id  = type_classname2classid[annotype]
            polarity_id  = polarity_classname2classid[polarity]
            intensity_id = intensity_classname2classid[intensity]

            if key not in input_output_dict:
                if   OUTPUT_FORMAT in ['t', 'p', 'i'] + OUTPUT_FORMATS['t|p|i:'] + OUTPUT_FORMATS['t,p,i:'] + OUTPUT_FORMATS['t|p|i='] + OUTPUT_FORMATS['t,p,i=']:
                    input_output_dict[key] = ''
                elif OUTPUT_FORMAT in ['t(ordered)']:
                    input_output_dict[key] = set()
                else:
                    print("OUTPUT FORMAT NOT SUPPORTED IN prepare_inputs_and_targets")
                n_samples += 1
            else:
                if   OUTPUT_FORMAT in ['t', 'p', 'i']:
                    input_output_dict[key] += ' '
                elif OUTPUT_FORMAT in ['t(ordered)']:
                    None
                elif OUTPUT_FORMAT in OUTPUT_FORMATS['t|p|i:'] + OUTPUT_FORMATS['t|p|i=']:
                    input_output_dict[key] += ' || '
                elif OUTPUT_FORMAT in OUTPUT_FORMATS['t,p,i:'] + OUTPUT_FORMATS['t,p,i=']:
                    input_output_dict[key] += ' | '
                else:
                    print("OUTPUT FORMAT NOT SUPPORTED IN prepare_inputs_and_targets")

            if   OUTPUT_FORMAT in ['t']:
                input_output_dict[key] += annotype_id
            elif OUTPUT_FORMAT in ['t(ordered)']:
                input_output_dict[key].add(annotype_id)
            elif OUTPUT_FORMAT in ['p']:
                input_output_dict[key] += polarity_id
            elif OUTPUT_FORMAT in ['i']:
                input_output_dict[key] += intensity_id
            elif OUTPUT_FORMAT in OUTPUT_FORMATS['t|p|i:'] + OUTPUT_FORMATS['t,p,i:'] + OUTPUT_FORMATS['t|p|i='] + OUTPUT_FORMATS['t,p,i=']:
                input_output_dict[key] += generate_text_cognitive_state(OUTPUT_FORMAT, annotype_id, polarity_id, intensity_id)
            else:
                print("OUTPUT FORMAT NOT SUPPORTED IN prepare_inputs_and_targets")

    if OUTPUT_FORMAT in ['t(ordered)']:
        for k in input_output_dict.keys():
            v = input_output_dict[k]
            list_v = list(v)
            text_v = list_v[0]
            for i in range(1, len(list_v)):
                text_v = text_v + ' ' + list_v[i]
            input_output_dict[k] = text_v

    return input_output_dict, n_samples


def save_dataset(X_text='', X_head='', y='', X_annotype='', output=None):
    task_prefix = CUSTOM_PREFIX
    if ADD_TASK_PREFIX:
        if   OUTPUT_FORMAT in OUTPUT_FORMATS['t']:
            task_prefix += 'type: '
        elif OUTPUT_FORMAT in OUTPUT_FORMATS['p']:
            task_prefix += 'polarity: '
        elif OUTPUT_FORMAT in OUTPUT_FORMATS['i']:
            task_prefix += 'intensity: '        
    
    pipe = ' | '
    if REMOVE_PIPES_FROM_INPUT:
        pipe = ' '

    if   INPUT_FORMAT in ['T:A|S']:
        X_pretokenized = [task_prefix + type_classname2classid[annotype] + ' : ' + head + pipe + text for annotype, head, text in zip(X_annotype, X_head, X_text)]
    elif INPUT_FORMAT in ['T:S|A']:
        X_pretokenized = [task_prefix + type_classname2classid[annotype] + ' : ' + text + pipe + head for annotype, head, text in zip(X_annotype, X_head, X_text)]
    elif INPUT_FORMAT in INPUT_FORMATS['T|A|S']:
        inner_separator = None
        if ':' in INPUT_FORMAT:
            inner_separator = ':'
        if '=' in INPUT_FORMAT:
            inner_separator = '='
        X_pretokenized = []
        for annotype, head, text in zip(X_annotype, X_head, X_text):
            X_pretokenized.append(task_prefix)
            for input_part in INPUT_FORMAT.split('|'):
                if X_pretokenized[-1] != task_prefix:
                    X_pretokenized[-1] += pipe
                if input_part[0] == 'T':
                    if inner_separator:
                        X_pretokenized[-1] += 'type ' + inner_separator + ' '
                    X_pretokenized[-1] += type_classname2classid[annotype]
                if input_part[0] == 'A':
                    if inner_separator:
                        X_pretokenized[-1] += 'aspect ' + inner_separator + ' '
                    X_pretokenized[-1] += head
                if input_part[0] == 'S':
                    if inner_separator:
                        X_pretokenized[-1] += 'sentence ' + inner_separator + ' '
                    X_pretokenized[-1] += text
    
    elif INPUT_FORMAT in ['A|S']:
        X_pretokenized = [task_prefix + head + pipe + text for head, text in zip(X_head, X_text)]
    elif INPUT_FORMAT in ['A:A|S:S']:
        X_pretokenized = [task_prefix + 'aspect : ' + head + pipe + 'sentence : ' + text for head, text in zip(X_head, X_text)]
    elif INPUT_FORMAT in ['A=A|S=S']:
        X_pretokenized = [task_prefix + 'aspect = ' + head + pipe + 'sentence = ' + text for head, text in zip(X_head, X_text)]
    elif INPUT_FORMAT in ['S|A']:
        X_pretokenized = [task_prefix + text + pipe + head for text, head in zip(X_text, X_head)]
    elif INPUT_FORMAT in ['S:S|A:A']:
        X_pretokenized = [task_prefix + 'sentence : ' + text + pipe + 'aspect : ' + head for text, head in zip(X_text, X_head)]
    elif INPUT_FORMAT in ['S=S|A=A']:
        X_pretokenized = [task_prefix + 'sentence = ' + text + pipe + 'aspect = ' + head for text, head in zip(X_text, X_head)]
    
    elif INPUT_FORMAT in ['S']:
        X_pretokenized = task_prefix + X_text
    elif INPUT_FORMAT in ['A']:
        X_pretokenized = task_prefix + X_head
    else:
        print("INPUT FORMAT NOT SUPPORTED IN tokenize_inputs")

    data = zip(X_pretokenized, y)

    with open(output, mode='w', newline='') as file:
        writer = csv.writer(file, lineterminator='\n')
        writer.writerow(['input', 'output'])  # Writing the header
        writer.writerows(data)


# Fetch the dataset
csds_collection = {}
with open('MPQA2.0_cleaned.json') as file:
    csds_collection = json.load(file)
csds_objects = csds_collection['csds_objects']
csds_splits = {}
with open('folds/tpi-folds.json') as file:
    csds_splits = json.load(file)

fold_keys = ['IDs_trainset_fold_1', 'IDs_validationset_fold_1', 'IDs_testset_fold_1']
train_ids = csds_splits[fold_keys[0]]
val_ids   = csds_splits[fold_keys[1]]
test_ids  = csds_splits[fold_keys[2]]

train_objects, val_objects, test_objects = filter_csds_objects_all(csds_objects, train_ids, val_ids, test_ids)

train_input_target_dict, n_train_samples = prepare_inputs_and_targets(train_objects)
val_input_target_dict,   n_val_samples   = prepare_inputs_and_targets(val_objects)
test_input_target_dict,  n_test_samples  = prepare_inputs_and_targets(test_objects)

X_train = list(train_input_target_dict.keys())
X_val   = list(val_input_target_dict.keys())
X_test  = list(test_input_target_dict.keys())

y_train = list(train_input_target_dict.values())
y_val   = list(val_input_target_dict.values())
y_test  = list(test_input_target_dict.values())

os.makedirs('./afl-subset/', exist_ok=True)

if INPUT_FORMAT in INPUT_FORMATS['T|A|S']:
    X_train_type, X_train_head, X_train_text = zip(*X_train)
    X_val_type,   X_val_head,   X_val_text   = zip(*X_val)
    X_test_type,  X_test_head,  X_test_text  = zip(*X_test)
    
    Xy_train_tokenized = save_dataset(list(X_train_text), list(X_train_head), y_train, list(X_train_type), output=f'./afl-subset/{OUTPUT_FORMAT}_train.csv')
    Xy_val_tokenized   = save_dataset(list(X_val_text), list(X_val_head), y_val, list(X_val_type), output=f'./afl-subset/{OUTPUT_FORMAT}_val.csv')
    Xy_test_tokenized  = save_dataset(list(X_test_text), list(X_test_head), y_test, list(X_test_type), output=f'./afl-subset/{OUTPUT_FORMAT}_test.csv')
    
elif INPUT_FORMAT in INPUT_FORMATS['A|S']:
    X_train_head, X_train_text = zip(*X_train)
    X_val_head,   X_val_text   = zip(*X_val)
    X_test_head,  X_test_text  = zip(*X_test)
    
    Xy_train_tokenized = save_dataset(list(X_train_text), list(X_train_head), y_train, output=f'./afl-subset/{OUTPUT_FORMAT}_train.csv')
    Xy_val_tokenized   = save_dataset(list(X_val_text), list(X_val_head), y_val, output=f'./afl-subset/{OUTPUT_FORMAT}_val.csv')
    Xy_test_tokenized  = save_dataset(list(X_test_text), list(X_test_head), y_test, output=f'./afl-subset/{OUTPUT_FORMAT}_test.csv')

print(f"Generated '{OUTPUT_FORMAT}' subset.")
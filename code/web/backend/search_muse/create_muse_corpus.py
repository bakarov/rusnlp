"""
python code/web/backend/search_muse/create_muse_corpus.py --texts_paths=texts/en_conllu+texts/ru_conllu --lemmatize=1 --embeddings_path=code/web/models/cross_muse_orig.bin.gz --common_vectors_path=code/web/models/common_lem_muse_orig.bin.gz --mis_path=texts/mis_lem_en_orig.txt+texts/mis_lem_ru_ext.orig --task_path=code/web/data/nlpub.tsv --task_column=terms_short --task_mis_path=texts/mis_lem_nlpub_orig.txt
python code/web/backend/search_muse/create_muse_corpus.py --texts_paths=texts/en_conllu+texts/ru_conllu --lemmatize=0 --embeddings_path=code/web/models/cross_muse_orig.bin.gz --common_vectors_path=code/web/models/common_tok_muse_orig.bin.gz --mis_path=texts/mis_tok_en_orig.txt+texts/mis_tok_ru_ext.orig --task_path=code/web/data/nlpub.tsv --task_column=terms_short --task_mis_path=texts/mis_tok_nlpub_orig.txt

python code/web/backend/search_muse/create_muse_corpus.py --texts_paths=texts/en_conllu+texts/ru_conllu --lemmatize=1 --embeddings_path=code/web/models/cross_muse_ext.bin.gz --common_vectors_path=code/web/models/common_lem_muse_ext.bin.gz --mis_path=texts/mis_lem_en_ext.txt+texts/mis_lem_ru_ext.txt --task_path=code/web/data/nlpub.tsv --task_column=terms_short --task_mis_path=texts/mis_lem_nlpub_ext.txt
python code/web/backend/search_muse/create_muse_corpus.py --texts_paths=texts/en_conllu+texts/ru_conllu --lemmatize=0 --embeddings_path=code/web/models/cross_muse_ext.bin.gz --common_vectors_path=code/web/models/common_tok_muse_ext.bin.gz --mis_path=texts/mis_tok_en_ext.txt+texts/mis_tok_ru_ext.txt --task_path=code/web/data/nlpub.tsv --task_column=terms_short --task_mis_path=texts/mis_tok_nlpub_ext.txt
"""

import argparse
import logging

from utils.loaders import load_embeddings, save_w2v, load_task_terms, split_paths
from utils.preprocessing import get_corpus
from utils.vectorization import vectorize_corpus

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)


def parse_args():
    parser = argparse.ArgumentParser(
        description='Векторизация корпусов в общую модель')
    parser.add_argument('--texts_paths', type=str, required=True,
                        help='Путь к текстам в формате conllu (можно перечислить через +)')
    parser.add_argument('--lemmatize', type=int, required=True,
                        help='Брать ли леммы текстов (0|1)')
    parser.add_argument('--keep_pos', type=int, default=0,
                        help='Возвращать ли слова, помеченные pos-тегами (0|1; default: 0)')
    parser.add_argument('--keep_punct', type=int, default=0,
                        help='Сохранять ли знаки препинания (0|1; default: 0)')
    parser.add_argument('--keep_stops', type=int, default=0,
                        help='Сохранять ли слова, получившие тег функциональной части речи '
                             '(0|1; default: 0)')
    parser.add_argument('--join_propn', type=int, default=0,
                        help='Склеивать ли именованные сущности (0|1; default: 0)')
    parser.add_argument('--join_token', type=str, default='::',
                        help='Как склеивать именованные сущности (default: ::)')
    parser.add_argument('--unite', type=int, default=1,
                        help='Убирать ли деление на предложения (0|1; default: 1)')
    parser.add_argument('--no_duplicates', type=int, default=0,
                        help='Брать ли для каждого типа в тексте вектор только по одному разу '
                             '(0|1; default: 0)')
    parser.add_argument('--substitute', type=int, default=0,
                        help='Брать ли слова, не найденного в модели, ближайшее имеющееся '
                             '(0|1; default: 0)')
    parser.add_argument('--max_end', type=int, default=3,
                        help='Максимальное окончание слова, которое убирается для поиска замены '
                             '(default: 3)')
    parser.add_argument('--embeddings_path', type=str, required=True,
                        help='Путь к модели векторизации')
    parser.add_argument('--common_vectors_path', type=str, required=True,
                        help='Путь к файлу, в котором лежит объединённый векторизованный корпус')
    parser.add_argument('--dir_vectors_paths', type=str,
                        help='Путь к файлу, в котором лежит векторизованный корпус из папки '
                             '(можно перечислить через +)')
    parser.add_argument('--mis_path', type=str,
                        help='Путь к файлу с ошибками векторизации текстов '
                             '(можно перечислить через +)')
    parser.add_argument('--task_path', type=str, required=True,
                        help='Путь к файлу с темами из NLPub')
    parser.add_argument('--task_column', type=str, default='terms',
                        help='Какую колонку со словами брать изNLPub (default: terms)')
    parser.add_argument('--task_mis_path', type=str,
                        help='Путь к файлу с ошибками векторизации задач NLPub')

    return parser.parse_args()


def main_onepath(texts_path, lemmatize, keep_pos, keep_punct, keep_stops, join_propn, join_token,
                 unite, embed_model, no_duplicates, substitute,  max_end, dir_vectors_path, mis_path):
    """делаем словарь векторов для папки"""
    # собираем тексты из conllu
    text_corpus = get_corpus(texts_path, lemmatize, keep_pos, keep_punct, keep_stops,
                             join_propn, join_token, unite)

    vec_corpus, not_vectorized = vectorize_corpus(text_corpus, embed_model, no_duplicates,
                                                  substitute,  max_end)

    if dir_vectors_path:
        save_w2v(vec_corpus, dir_vectors_path)

    if not_vectorized:
        logging.info('Not vectorized texts: {}'.format(len(not_vectorized)))
        if mis_path:
            open(mis_path, 'w', encoding='utf-8').write('\n'.join(not_vectorized))

    return vec_corpus


def main():
    args = parse_args()

    texts_paths = args.texts_paths.split('+')
    dir_vectors_paths = split_paths(args.dir_vectors_paths, texts_paths)
    mis_paths = split_paths(args.mis_path, texts_paths)

    embed_model = load_embeddings(args.embeddings_path)
    common_vectors = {}

    for texts_path, dir_vectors_path, mis_path in zip(texts_paths, dir_vectors_paths, mis_paths):
        logging.info('Vectorizing {}...'.format(texts_path))
        text_vectors = main_onepath(texts_path, args.lemmatize, args.keep_pos, args.keep_punct,
                                    args.keep_stops, args.join_propn, args.join_token, args.unite,
                                    embed_model, args.no_duplicates, args.substitute,  args.max_end,
                                    dir_vectors_path, mis_path)

        common_vectors.update(text_vectors)

    task_terms = load_task_terms(args.task_path, args.task_column)
    logging.info('Vectorizing tasks...')
    task_vectors, not_vectorized = vectorize_corpus(task_terms, embed_model, args.substitute,  args.max_end)
    if not_vectorized:
        logging.info('Not vectorized tasks: {}'.format(len(not_vectorized)))
        if args.task_mis_path:
            open(args.task_mis_path, 'w', encoding='utf-8').write('\n'.join(not_vectorized))
    common_vectors.update(task_vectors)

    save_w2v(common_vectors, args.common_vectors_path)


if __name__ == "__main__":
    main()

import argparse
import sys
import pandas as pd

class DoubleError(Exception):
    pass

def merge_annotations(current_file, new_file, to_csv=False, result_name='my_result.tsv'):
    """
    Merging annotated authors\affilations with previous result.
    It is better to make result name with .tsv format.
    """
    # old_file, new_file, result_name = sys.argv[1:]

    old_df = pd.read_csv(current_file, sep='\t', names=['index', 'dict_name', 'name_variants'])
    new_df = pd.read_csv(new_file, sep='\t', names=['text', 'name_variants', 'index', 'dict_name'])
    format_new_df = new_df[['index', 'dict_name', 'name_variants']]

    merged_df = pd.concat([old_df, format_new_df])
    merged_df.sort_values('index')

    for i in set(merged_df['index']):
        pass
        temp_df = merged_df[merged_df['index'] == i]
        if len(set(temp_df['dict_name'])) > 1:
            raise DoubleError(f"Different affilations/authors with same id occured!"
                              f"Please, check {set(temp_df['dict_name'])}"
                              f"id: {i} ")

    merged_df.to_csv(result_name, index=False, sep ='\t')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    arg = parser.add_argument
    arg("--current_file", "-c", help="Path to current affiliations or authors",
        type=str,
        required=True)
    arg("--new_file", "-n", help="Path to annotated file",
        type=str,
        required=True)
    arg("--to_csv", "-t", help="You can just add this key with any argument to switch"
                               "from false to true if you need csv-file result",
        type=bool,
        required=False)
    arg("--result_file", "-r", help="You can add result file name(path), result.tsv by default",
        type=str,
        required=False)

    args = parser.parse_args()
    old_file = args.current_file
    new_file = args.new_file
    result_name = args.result_file
    to_csv = args.to_csv

    if new_file and result_name:
        merge_annotations(old_file, new_file, to_csv=to_csv, result_name=result_name)
    elif new_file and not result_name:
        merge_annotations(old_file, new_file, to_csv=new_file)
    else:
        merge_annotations(old_file, new_file)
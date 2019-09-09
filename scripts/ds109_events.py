from pathlib import Path
from numpy import nan
import pandas as pd

#This script transforms ds000109 events files into a format that is easily readable
#By our primary analysis scripts. Run 1 and Run 2 events files are differently formatted
#So a subfunction was defined to convert Run 2 files into the Run 1 format

if __name__ == '__main__':
    from argparse import ArgumentParser
    from argparse import RawTextHelpFormatter

    parser = ArgumentParser(description='DS000109 Analysis Workflow',
                            formatter_class=RawTextHelpFormatter)

    parser.add_argument('in_file', action='store', type=Path,
                        help='the input events file we want to fix')

    #parse the input file as an option
    opts = parser.parse_args()

    #Read in the events file. It pulls in onset, duration and trial_type, which are the only
    #Values needed for our analysis
    original_df = pd.read_csv(opts.in_file, sep='\t', na_values="n/a",
                              dtype={'onset': float, 'duration': float,
                                     'trial_type': str})

    #create a duplicate of the input file with the extension .bak as a backup ;)
    opts.in_file.rename('%s.bak' % opts.in_file)

    tt_names = original_df[~original_df.trial_type.isnull()]
    working_df = original_df[original_df.trial_type.isnull()]

    #if the input file is for run 2, convert it to run 1 format
    if 'run-02' in opts.in_file:
        working_df = run2processing(working_df)

    working_df = working_df[working_df.trial_type.isnull()].set_index('onset')

    #this is where the magic happens
    for tt in set(tt_names.trial_type.values):
        rows = tt_names[tt_names.trial_type == tt]
        for _, row in rows.iterrows():
                onset = row.onset
                end = (onset + row.duration) - 2.0
                working_df.loc[onset:end, 'trial_type'] = tt

    working_df[working_df.trial_type == 0.0] = nan

    working_df.to_csv(opts.in_file, sep='\t', na_rep='n/a')

#A function that handle the formatting differences between run 1 and run 2 events files
#by converting run 2 event files to match the run 1 formatting
def run2processing(working_df):

    #define baseline_onset as the lowest value in the onset column of the data frame
    baseline_onset = working_df.iloc[working_df["onset"].idxmin()]["onset"]

    #create a duplicate of working_df to mutate
    run2_df = working_df

    #subtract the baseline onset from the entire onset column
    run2_df["onset"] = working_df["onset"] - baseline_onset

    #return mutated dataframe
    return run2_df

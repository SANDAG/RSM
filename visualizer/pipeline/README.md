# Data Pipeline Tool

The Data Pipeline Tool aims to aid in the process of building data pipelines that ingest, transform, and summarize data by taking advantage of the parameterization of data pipelines. Rather than coding from scratch, configure a few files and the tool will figure out the rest.

## Background

Data pipelines across projects can vary heavily in terms of the data that is used, how the data is transformed, and the eventual summaries that are required and produced. However, the fundamental ways to develop these data pipelines, from a technical perspective, tend to overlap. For example, in Python, one may repeatedly use *pd.read_csv()* to read in data or *pd.merge()* to combine data sets. Ultimately, these pipelines, to a certain degree, can be parameterized to minimize redundancy in implementation. This is precisely the reason for the creation of this tool.

## Configuring A Pipeline

To configure your data pipeline, you will need to edit the following three files in the `config` directory:

- `settings.yaml`: Main settings file for the tool. Controls the overall flow of the data pipeline.

- `processor.csv`: Contains expressions that are used to process data before or after summarization.

- `expressions.csv`: Contains expressions to summarize data and controls how summary tables are written upon tool completion.

- `user_added_functions.py`: Contains user-defined functions that can be called in the processor.

The following describes the contents of these files and how they can be edited.

### `settings.yaml`

This file consists of the following properties. Please see [this](config/settings.yaml) for an example.

- `extract`: Root property -- controls data extraction (reading). Note: Multiple data sources can be specified by the user.

  - `filepath` (str): File path to data source
  - `test_size` (int): Number of rows to read from input data -- for testing purposes. Leave empty to read all rows.
  - `data`: List of files at the specified data *filepath* to read

- `transform`: Root property -- controls data processing.
  - `processor` (str): File path to processor specification file
  - `expressions` (str):  File path to summary expressions specification file
  - `steps`: Lists the processing steps to execute. Note: User can create as many necessary steps. The order of processing, concatenating, and merging that is specified will be followed for each step.
    - `name` (str): User-defined name of processing step
    - `process` (bool): True or False -- whether to run processor. Note: Only the processor expressions corresponding to a step will be executed
    - `summarize`: (bool): True or False -- whether to run summarizer. Note: This property should only be called **once**. Once called, only the tables resulting from the summary expressions will be available for post-processing.
    - `concat`: Controls data concatenation
      - `table_name` (str): User-defined name of resulting table after concatenation
      - `include`: List of data set names to concatenate. Note: Names are either those loaded in *extract* without the file extension or the user-defined names resulting from a previous concatenation or merge.
    - `merge`: Controls data merging
      - `table_name` (str): User-defined name of resulting table after merge
      - `include`: List of data set names to merge. Note: Names are either those loaded in *extract* without the file extension or the user-defined names resulting from a previous concatenation or merge.
      - `merge_cols`: List of columns to merge two data sets on. Note: The order of the columns must match the order specified in *in
      - `merge_type` (str): Merge type -- 'left', 'right', 'inner', or 'outer' merge are supported

- `load`: Root property -- controls results loading/writing
  - `outdir` (str): File path of directory to write results to
  - `empty_fill` (str or numeric): Value to use for filling missing values in output results

### `processor.csv`

This file consists of the following fields. Please see [this](config/processor.csv) for an example.

- `Description`: User-specified description of what the processing row accomplishes
- `Step`: User-defined *processing step* name that the row belongs to
- `Type`: Processing type of the row
  - `column`: Generate a new field from a combination of fields or a transformation of a field in *Table* as defined by *Func*. Note: User does not need to specify *In Col* if used.
  - `rename`: Rename field(s) as defined by the dictionary in *Func*. Note: User does not need to specify *In Col* or *Out Col* if used.
  - `replace`: Replace values in a field as defined by the dictionary in *Func*
  - `bin`: Bin values in a field into discrete values as defined by the intervals in *Func*
  - `cap`: Cap values in a field to a maximum value specified in *Func*
  - `apply`: Apply a Pandas Series apply() function to every element in a field as defined by *Func*. Note: Function should be written as if writing directly within apply().
  - `sum`: Take the row-wise sum of multiple columns as specified by comma delimited names in *In Col*. Note: User does not need to specify *Func* if used.
  - `skim`: Query skim (.omx) origin-destination pairs as specified by the comma delimited pairs in *In Col* and the skim matrix specified in *Func*
  - `raw`: Evaluate raw Python expression as defined by *Func*. Note: User does not need to specify *In Col*, *Out Col*, or *Table* if used.
- `Table`: Name of the table to evaluate the processor row on. Note: Names are either those loaded in *extract* without the file extension or the user-defined names resulting from a previous concatenation or merge.
- `Out Col`: Field name of processing result -- added to *Table*
- `In Col`: Field name of fie*Table* to apply processing
- `Func`: Function/expression to use for processing

### `expressions.csv`

This file consists of the following fields. Please see [this](config/expressions.csv) for an example.

- `Description`: User-specified description of what the summarization row accomplishes
- `Out Table`: User-defined summary table name to add result to. Npte: Unique set of table names in this column will be written out upon the tools completion.
- `Out Col`: Field name of expression result -- added to *Out Table*
- `In Table`: Name of the table to evaluate the expression on. Note: Names are either those loaded in *extract* without the file extension or the user-defined names resulting from a previous concatenation or merge.
- `Filter`: Pandas query filter to apply to *In Table* before evaluating expression
- `In Col`: Field name of field in *In Table* to apply expression
- `Func`: Pandas Series method to apply to *In Col* as defined by the [Pandas API](https://pandas.pydata.org/docs/reference/api/pandas.Series.html). Users can also specify a custom Python expression using the *Out Col* names of expressions previously evaluated (much like a measure in PowerBI) -- for such cases, *In Col*, *Filter*, and *In Table* do not need to be specified.
- `Group`: Comma delimited field names of fields in *In Table* to use for group aggregations

### `user_added_functions.py`

Any function defined in this script will be able to be called in the processor.

## Running A Pipeline

To run the configured pipeline, do the following:

1. Open Anaconda 3 Prompt
2. Create an Anaconda environment using the provided environment.yml file: `conda env create -f environment.yml`
3. Activate the newly created environment: `conda activate pipeline`
4. Change directory to the project folder
5. Configure the data pipeline as described in *Configuring A Pipeline*
6. Run the tool by executing the following: `python run.py`
7. When the process finishes, all resulting summary files are written to the output directory specified in `settings.yaml`

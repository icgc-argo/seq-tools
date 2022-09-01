# Scenarios and tests for validating sequencing data

## Categories
### Metadata Payload Sanity Check
#### [c110_rg_id_uniqueness](#c110_rg_id_uniqueness)
#### [c120_permissible_char_in_rg_id](#c120_permissible_char_in_rg_id)
#### [c130_one_sample](#c130_one_sample)
#### [c140_platform_unit_uniqueness](#c140_platform_unit_uniqueness)
#### [c150_rg_count_match](#c150_rg_count_match)
#### [c160_file_r1_r2_check](#c160_file_r1_r2_check)
#### [c170_fq_uniqueness_in_rgs](#c170_fq_uniqueness_in_rgs)
#### [c180_file_uniqueness](#c180_file_uniqueness)
#### [c190_no_extra_files](#c190_no_extra_files)
#### [c200_rg_id_in_bam_uniqueness](#c200_rg_id_in_bam_uniqueness)
#### [c210_no_path_in_filename](#c210_no_path_in_filename)
#### [c220_no_rg_id_in_bam_for_fq](#c220_no_rg_id_in_bam_for_fq)
#### [c230_files_info_data_category](#c230_files_info_data_category)
#### [c240_submitter_rg_id_collide_with_rg_id_in_bam](#c240_submitter_rg_id_collide_with_rg_id_in_bam)
#### [c250_file_data_type](#c250_file_data_type)
#### [c260_filename_pattern](#c260_filename_pattern)


### File integrity
#### [c608_bam_sanity](#c608_bam_sanity)
#### [c609_fastq_sanity](#c608_fastq_sanity)
#### [c681_fileSize_match](#c681_fileSize_match)
#### [c683_fileMd5sum_match](#c683_fileMd5sum_match)

### Metadata and Molecular Data Correspondence
#### [c610_rg_id_in_bam](#c610_rg_id_in_bam)
#### [c620_submitter_read_group_id_match](#c620_submitter_read_group_id_match)
#### [c630_rg_id_in_bam_match](#c630_rg_id_in_bam_match)
#### [c640_one_sm_in_bam_header](#c640_one_sm_in_bam_header)
#### [c650_sm_in_bam_matches_metadata](#c650_sm_in_bam_matches_metadata)
#### [c660_metadata_in_bam_rg_header](#c660_metadata_in_bam_rg_header)
#### [c670_rg_is_paired_in_bam](#c670_rg_is_paired_in_bam)
#### [c680_repeated_read_names_per_group_in_bam](#c680_repeated_read_names_per_group_in_bam)


### RNA-Seq
#### [c690_check_strand_specificity_in_bam](#c690_check_strand_specificity_in_bam)
#### [c691_check_strand_specificity_in_fastq](#c691_check_strand_specificity_in_fastq)

## Tests
#### <a id=c110_rg_id_uniqueness>[c110_rg_id_uniqueness](https://github.com/icgc-argo/seq-tools/tree/main/seq_tools/validation/c110_rg_id_uniqueness.py)</a>:
- Verifies each `read_group` has an unique `submitter_read_group_id` value
#### <a id=c120_permissible_char_in_rg_id>[c120_permissible_char_in_rg_id](https://github.com/icgc-argo/seq-tools/tree/main/seq_tools/validation/c120_permissible_char_in_rg_id.py)</a>:
- Verifies `submitter_read_group_id` per `read_group` conforms to regex: 
```
^[a-zA-Z0-9\\-_:\\.]+$
```
#### <a id=c130_one_sample>[c130_one_sample](https://github.com/icgc-argo/seq-tools/tree/main/seq_tools/validation/c130_one_sample.py)</a>:
- Verifies metadata payload contains only one sample
#### <a id=c140_platform_unit_uniqueness>[c140_platform_unit_uniqueness](https://github.com/icgc-argo/seq-tools/tree/main/seq_tools/validation/c140_platform_unit_uniqueness.py)</a>:
- Verifies each `read_group` has an unique `platform_unit` value
#### <a id=c150_rg_count_match>[c150_rg_count_match](https://github.com/icgc-argo/seq-tools/tree/main/seq_tools/validation/c150_rg_count_match.py)</a>:
- Verifies the number of `read_group`s equals `read_group_count`
#### <a id=c160_file_r1_r2_check>[c160_file_r1_r2_check](https://github.com/icgc-argo/seq-tools/tree/main/seq_tools/validation/c160_file_r1_r2_check.py)</a>:
- Verifies each `read_group` record has a value `is_paired_end` and :
- If `is_paired_end`==`True`: `file_r1` and `file_r2` is populated.
- If `is_paired_end`==`False` only `file_r1` is populated
#### <a id=c170_fq_uniqueness_in_rgs>[c170_fq_uniqueness_in_rgs](https://github.com/icgc-argo/seq-tools/tree/main/seq_tools/validation/c170_fq_uniqueness_in_rgs.py)</a>:
- Verifies that each FASTQ provided is uniquely named
#### <a id=c180_file_uniqueness>[c180_file_uniqueness](https://github.com/icgc-argo/seq-tools/tree/main/seq_tools/validation/c180_file_uniqueness.py)</a>:
- Verifies each entry in `files` section is uniquely named
#### <a id=c190_no_extra_files>[c190_no_extra_files](https://github.com/icgc-argo/seq-tools/tree/main/seq_tools/validation/c190_no_extra_files.py)</a>:
- Verifies each entry in the `files` section is mentioned in `read_groups` section and no additional files exist
#### <a id=c200_rg_id_in_bam_uniqueness>[c200_rg_id_in_bam_uniqueness](https://github.com/icgc-argo/seq-tools/tree/main/seq_tools/validation/c200_rg_id_in_bam_uniqueness.py)</a>:
- Verifies each `read_group` has an unique `read_group_id_in_bam` value
#### <a id=c210_no_path_in_filename>[c210_no_path_in_filename](https://github.com/icgc-argo/seq-tools/tree/main/seq_tools/validation/c210_no_path_in_filename.py)</a>:
- Verifies each `files` consists of only basename and no path 
#### <a id=c220_no_rg_id_in_bam_for_fq>[c220_no_rg_id_in_bam_for_fq](https://github.com/icgc-argo/seq-tools/tree/main/seq_tools/validation/c220_no_rg_id_in_bam_for_fq.py)</a>:
- Verifies that `read_group_id_in_bam` is not populated when `read_group` consist of FASTQ files
#### <a id=c230_files_info_data_category>[c230_files_info_data_category](https://github.com/icgc-argo/seq-tools/tree/main/seq_tools/validation/c230_files_info_data_category.py)</a>:
- Verifies each entry of `files` has:
```
'info':{
    'data_category': 'Sequencing_Reads'
}
```
#### <a id=c240_submitter_rg_id_collide_with_rg_id_in_bam>[c240_submitter_rg_id_collide_with_rg_id_in_bam](https://github.com/icgc-argo/seq-tools/tree/main/seq_tools/validation/c240_submitter_rg_id_collide_with_rg_id_in_bam.py)</a>:
- Verifies that when a `read_group`'s `read_group_id_in_bam` is not provided, the corresponding `submitter_read_group_id` does not match other `read_group_id_bam`s within the BAM file
#### <a id=c250_file_data_type>[c250_file_data_type](https://github.com/icgc-argo/seq-tools/tree/main/seq_tools/validation/c250_file_data_type.py)</a>:
- Verifies each entry of `files` contains:
```
'dataType':'Submitted Reads'
```
#### <a id=c260_filename_pattern>[c260_filename_pattern](https://github.com/icgc-argo/seq-tools/tree/main/seq_tools/validation/c260_filename_pattern.py)</a>:
- Verfies provided `files` are appropriately typed and conforms to the following regex:
```
^[A-Za-z0-9]{1}[A-Za-z0-9_\.\-]*\.(bam|fq\.gz|fastq\.gz|fq\.bz2|fastq\.bz2)$'
```
#### <a id=c605_all_files_accessible>[c605_all_files_accessible](https://github.com/icgc-argo/seq-tools/tree/main/seq_tools/validation/c605_all_files_accessible.py)</a>:
- Verifies provided `files` can be found in the provided data directory or in the same directory as metadata payload
#### <a id=c608_bam_sanity>[c608_bam_sanity](https://github.com/icgc-argo/seq-tools/tree/main/seq_tools/validation/c608_bam_sanity.py)</a>:
- Verifies provided BAM `files` follow BAM file format standards
#### <a id=c608_fastq_sanity>[c609_fastq_sanity](https://github.com/icgc-argo/seq-tools/tree/main/seq_tools/validation/c609_fastq_sanity.py)</a>:
- Verifies provided FASTQ `files` follow FASTQ file format standards
#### <a id=c610_rg_id_in_bam>[c610_rg_id_in_bam](https://github.com/icgc-argo/seq-tools/tree/main/seq_tools/validation/c610_rg_id_in_bam.py)</a>:
- Verifies `ID`s in BAM header exist, are unique and conform to the following regex:
```
^[0-9a-zA-Z-_:\'\.\+]+$
```
#### <a id=c620_submitter_read_group_id_match>[c620_submitter_read_group_id_match](https://github.com/icgc-argo/seq-tools/tree/main/seq_tools/validation/c620_submitter_read_group_id_match.py)</a>:
- Verifies provided `submitter_read_group_id` matches `ID` found in BAM header when `read_group_id_in_bam` not provided.
#### <a id=c630_rg_id_in_bam_match>[c630_rg_id_in_bam_match](https://github.com/icgc-argo/seq-tools/tree/main/seq_tools/validation/c630_rg_id_in_bam_match.py)</a>:
- Verifies `read_group_id_in_bam` matches `ID` found in BAM header.
#### <a id=c640_one_sm_in_bam_header>[c640_one_sm_in_bam_header](https://github.com/icgc-argo/seq-tools/tree/main/seq_tools/validation/c640_one_sm_in_bam_header.py)</a>:
- Verifies only `SM` entry exists in BAM header.
#### <a id=c650_sm_in_bam_matches_metadata>[c650_sm_in_bam_matches_metadata](https://github.com/icgc-argo/seq-tools/tree/main/seq_tools/validation/c650_sm_in_bam_matches_metadata.py)</a>:
- Verifies `submitterSampleId` matches `SM` entry in BAM header.
#### <a id=c660_metadata_in_bam_rg_header>[c660_metadata_in_bam_rg_header](https://github.com/icgc-argo/seq-tools/tree/main/seq_tools/validation/c660_metadata_in_bam_rg_header.py)</a>:
- Verifies the following BAM header fields match metadata payload fields

|BAM Header field|Metadata Payload Field|
|-|-|    
|BC|sample_barcode|
|CN|sequencing_center|
|DT|sequencing_date|
|LB|library_name|
|PI|insert_size|
|PL|platform|
|PM|platform_model|
|PU|platform_unit|
- A warning will produced if differences are detected
- Info in metadata payload will be prioritized
#### <a id=c670_rg_is_paired_in_bam>[c670_rg_is_paired_in_bam](https://github.com/icgc-argo/seq-tools/tree/main/seq_tools/validation/c670_rg_is_paired_in_bam.py)</a>:
- Per `read_group`, verifies `is_paired_end` status in BAM files
#### <a id=c680_repeated_read_names_per_group_in_bam>[c680_repeated_read_names_per_group_in_bam](https://github.com/icgc-argo/seq-tools/tree/main/seq_tools/validation/c680_repeated_read_names_per_group_in_bam.py)</a>:
- Per first 500,000 entries in BAM, verifies if `read_name` is duplicated or exists in another `read_group` within the same BAM
#### <a id=c681_fileSize_match>[c681_fileSize_match](https://github.com/icgc-argo/seq-tools/tree/main/seq_tools/validation/c681_fileSize_match.py)</a>:
- Verifies each entry in `files`'s `size` (bytes) matches size in metadata payload
#### <a id=c683_fileMd5sum_match>[c683_fileMd5sum_match](https://github.com/icgc-argo/seq-tools/tree/main/seq_tools/validation/c683_fileMd5sum_match.py)</a>:
- Verifies each entry in `files`'s `Md5sum` matches Md5 in metadata payload

#### <a id=c690_check_strand_specificity_in_bam>[c690_check_strand_specificity_in_bam](https://github.com/icgc-argo/seq-tools/tree/main/seq_tools/validation/c690_check_strand_specificity_in_bam.py)</a>:
- If `experiment_strategy`==`RNA-seq`, verifies `library_strandedness` matches alignment in BAMs
#### <a id=c691_check_strand_specificity_in_fastq>[c691_check_strand_specificity_in_fastq](https://github.com/icgc-argo/seq-tools/tree/main/seq_tools/validation/c691_check_strand_specificity_in_fastq.py)</a>:
- If `experiment_strategy`==`RNA-seq`, verifies `library_strandedness` matches alignment in subsampled and aligned FASTQs
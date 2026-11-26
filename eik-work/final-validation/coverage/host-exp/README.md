# Host exp coverage

The audit selected the single frozen trial report for chunks [0, 4096), where each
chunk contains 2²⁰ consecutive binary32 words. The checker covered all
4,294,967,296 words in 481 reported seconds. The checker and wrapper both exited
zero, with both completeness flags true, zero mismatches, and empty stderr.

The freeze manifest binds the root source, trial source, packet, and evaluator
fingerprint. The trial packet binds the original commands and all three raw files
for each run. The fingerprint command and fullcheck use the same runner-managed
Python installation. The retained cold replay independently reproduced the
fingerprint output byte for byte and recorded GCC 13.3.0 and Python 3.12.3. The
pinned runner selects GCC by default through the pinned kit configuration. The
pinned kit compiles and links the host checker with
`-fsanitize=undefined,address -fno-sanitize-recover=all`. Its fullcheck stage
sets fatal sanitizer exits and checks each output chunk against the pinned
reference digest. The retained command has no sampling option.

The runtime binding is at the kit fingerprint level. The original host
executable and loaded sanitizer libraries have no retained byte hashes. The
recorded cold replay is corroboration of the tool identity and does not extend
the word count. This audit reuses the original logs and did not run a new
exhaustive check or assess target images.

Run `python3 eik-work/final-validation/coverage/host-exp/verify.py` from the
repository root. It uses only the Python standard library and checks the committed
evidence in place. It accepts the one audited whole-domain range, so any missing,
partial, overlapping, or extra range invalidates the coverage claim.

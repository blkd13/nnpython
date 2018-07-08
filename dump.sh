#!/bin/sh
time psql mydb -A -F , -q -P footer=off -c \
				"SELECT race_id,kumiban,atari,odds1,ninki1,odds1e FROM odds_list_koushiki WHERE race_id<'20180231-01-01' ORDER BY race_id,kumiban" \
				-o odds_list_koushiki.csv

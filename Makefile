venv:
	virtualenv -p $(shell which python3) venv
	venv/bin/pip install -r requirements.txt

pull:
	@echo 'https://www.dhs.gov/immigration-statistics/yearbook/2019#*'
	wget -q 'https://www.dhs.gov/sites/default/files/publications/immigration-statistics/yearbook/2019/yrbk_2019_lpr_excel_final.zip'
	wget -q 'https://www.dhs.gov/sites/default/files/publications/immigration-statistics/yearbook/2019/yrbk_2019_rfa_excel_final.zip'
	wget -q 'https://www.dhs.gov/sites/default/files/publications/immigration-statistics/yearbook/2019/yrbk_2019_natz_excel_final.zip'
	wget -q 'https://www.dhs.gov/sites/default/files/publications/immigration-statistics/yearbook/2019/yrbk_2019_ni_excel_final.zip'
	wget -q 'https://www.dhs.gov/sites/default/files/publications/immigration-statistics/yearbook/2019/yrbk_2019_enf_excel_final.zip'
	find -maxdepth 1 -name '*.zip' -exec 'unzip' '{}' ';'
	wget 'https://trac.syr.edu/phptools/immigration/remove/graph.php?stat=count&timescale=fymon&depart_state=2&timeunit=number' -O trac.json

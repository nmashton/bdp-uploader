# -*- coding: utf-8 -*-

from app.bdp import app
from utils.csv import BudgetCSV
from functools import reduce
from copy import copy
import json
import os

bundleable = [
    ["admin","adminID","adminOrgID"],
    ["economic","economicID"],
    ["functional","functionalID"],
    ["fund","fundID"],
    ["program","programID"],
    ["project","projectID"],
    ["purchaserID","purchaserOrgID"]
]

model_map_file = os.path.join(app.config['DATA'], 'model-map.json')
with open(model_map_file) as mm_js:
    model_map = json.loads(mm_js.read())

class BDP(object):
    """
    A simple Budget Data Package, including both data and
    metadata.

    This version assumes that the BDP includes only a single
    dataset.
    """

    def __init__(self, dataset_file, metadata_file):
        self.dataset_file = dataset_file
        self.csv = BudgetCSV(open(dataset_file))

        self.metadata_file = metadata_file
        with open(metadata_file) as metadata:
            self.metadata = json.loads(metadata.read())

    def _get_model_fields(self):
        """
        Returns the processed list of fields that will end up
        in the model file.
        """
        fields = self.csv._get_headers()
        return bundle_all(fields,bundleable)

    def _get_dataset_attribute(self):
        """
        Returns the `dataset` attribute that can be extracted
        from the metadata.
        """
        m = self.metadata
        return {
            "name": m["name"],
            "currency": m["resources"][0]["currency"]
        }

    def prepare_csv(self):
        """
        Does what's necessary to get the CSV ready for OS upload.
        """
        fields = self.csv._get_headers()
        if cofog_pred(fields):
            self.csv.append_columns(
                ["cofog1","cofog2","cofog3"],
                split_cofog)
        if gfsm_expenditure_pred(fields):
            self.csv.append_columns(
                ["gfsmExpenditure1",
                 "gfsmExpenditure2",
                 "gfsmExpenditure3",
                 "gfsmExpenditure4",
                 "gfsmExpenditure5"],
                 split_gfsm_expenditure)
        if gfsm_revenue_pred(fields):
            self.csv.append_columns(
                ["gfsmRevenue1",
                 "gfsmRevenue2",
                 "gfsmRevenue3",
                 "gfsmRevenue4"],
                 split_gfsm_revenue)

    def make_model(self):
        """
        Returns the JSON model glob that can be used to upload
        to OpenSpending.
        """
        mapping_fields = self._get_model_fields()
        mapping = map(lambda f: model_map[f], model_fields)
        dataset = self._get_dataset_attribute()
        model = {
            "mapping": mapping,
            "dataset": dataset
        }
        return json.dumps(model)

def mapping(fields):
    """
    Takes a list of fields.
    Returns the `mapping` attribute of an OpenSpending model.
    """
    my_mapping = {}
    for field in fields:
        if field in model_map.keys():
            my_mapping[field] = model_map[field]
    return my_mapping

def bundle(headers, to_bundle):
    """
    Takes a headers list and a list of headers to be bundled
    together.

    Returns a new headers list with the to-be-bundled items
    removed and the bundled item added.
    """

    items_present = filter(lambda h: h in headers, to_bundle)
    if len(items_present) == 0:
        return headers

    result = copy(headers)
    for item in items_present:
        result.remove(item)

    result.append(" + ".join(items_present))
    return result

def bundle_all(headers, bundles):
    """
    Applies bundle() with a whole list of to_bundle items.
    """
    return reduce(bundle,bundles,headers)

def cofog_pred(headers):
    """
    Checks if a list of headers is such that `cofog` should
    be split out.
    """
    return not ("cofog" not in headers
        or "cofog1" in headers
        or "cofog2" in headers
        or "cofog3" in headers)

def gfsm_expenditure_pred(headers):
    """
    Checks if a list of headers is such that `gfsmExpenditure`
    should be split out.
    """
    return not ("gfsmExpenditure" not in headers
        or "gfsmExpenditure1" in headers
        or "gfsmExpenditure2" in headers
        or "gfsmExpenditure3" in headers
        or "gfsmExpenditure4" in headers
        or "gfsmExpenditure5" in headers)

def gfsm_revenue_pred(headers):
    """
    Checks if a list of headers is such that `gfsmRevenue`
    should be split out.
    """
    return not ("gfsmRevenue" not in headers
        or "gfsmRevenue1" in headers
        or "gfsmRevenue2" in headers
        or "gfsmRevenue3" in headers
        or "gfsmRevenue4" in headers)

def split_cofog(row):
    """
    Takes a DictReader row dictionary and returns a dictionary
    that splits the row's "cofog" value into three columns.
    """
    cofog_value = row["cofog"]
    cofog_list = cofog_value.split(".")
    length = len(cofog_list)
    # make sure the list isn't too long
    if length > 3:
        raise ValueError("Input COFOG value has too many sublevels (" + str(length) + ")")
    # pad the list if it's too short
    if length < 3:
        for _ in range(3 - length):
            cofog_list.append("")
    # create the result dictionary
    result = {}
    for i in range(3):
        result["cofog" + str(i+1)] = cofog_list[i]
    return result

def split_gfsm(row,type):
    """
    Takes a DictReader row dictionary and returns a dictionary
    that splits the row's "gfsmExpenditure" or "gfsmRevenue",
    given by `type`.
    """
    target = "gfsm" + type
    gfsm_value = row[target]
    gfsm_list = gfsm_value.split('.')
    length = len(gfsm_list)
    if type == "Revenue":
        ideal_length = 5
    else:
        ideal_length = 4
    if length > ideal_length:
        raise ValueError("Input GFSM value has too many sublevels (" + str(length) + ")")
    if length < ideal_length:
        for _ in range(ideal_length - length):
            gfsm_list.append("")
    result = {}
    for i in range(ideal_length):
        result["gfsm" + type + str(i+1)] = gfsm_list[i]
    return result

split_gfsm_expenditure = lambda r: split_gfsm(r, "Expenditure")
split_gfsm_revenue = lambda r: split_gfsm(r, "Revenue")
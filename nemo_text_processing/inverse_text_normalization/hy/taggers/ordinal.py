# Copyright (c) 2024, NVIDIA CORPORATION.  All rights reserved.
# Copyright 2015 and onwards Google, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import pynini
from nemo_text_processing.inverse_text_normalization.hy.utils import get_abs_path
from nemo_text_processing.text_normalization.en.graph_utils import NEMO_CHAR, GraphFst, INPUT_LOWER_CASED, INPUT_CASED, capitalized_input_graph
from pynini.lib import pynutil


class OrdinalFst(GraphFst):
    """
    Finite state transducer for classifying ordinal
        e.g. հիսունյոթերորդ -> tokens { ordinal { integer: "57" } }

    Args:
        cardinal: CardinalFst
        input_case: accepting either "lower_cased" or "cased" input.
        (input_case is not necessary everything is made for lower_cased input)
        TODO add cased input support
    """
    def __init__(self, cardinal: GraphFst, input_case: str = INPUT_LOWER_CASED):
        super().__init__(name="ordinal", kind="classify")

        cardinal_graph = cardinal.graph_no_exception
        graph_digit = pynini.string_file(get_abs_path("data/ordinals/digit.tsv"))
        graph = pynini.closure(NEMO_CHAR) + pynini.union(
            graph_digit, pynini.cross("երորդ", "")
        )

        self.graph = pynini.compose(graph, cardinal_graph).optimize()

        if input_case == INPUT_CASED:
            self.graph = capitalized_input_graph(self.graph)

        final_graph = pynutil.insert("integer: \"") + self.graph + pynutil.insert("\"")
        final_graph = self.add_tokens(final_graph)
        self.fst = final_graph.optimize()

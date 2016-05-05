# encoding: utf-8

"""
Data label-related oxml objects.
"""

from __future__ import (
    absolute_import, division, print_function, unicode_literals
)

from .. import parse_xml
from ...enum.chart import XL_DATA_LABEL_POSITION
from ..ns import nsdecls
from ..text import CT_TextBody
from ..xmlchemy import (
    BaseOxmlElement, OneAndOnlyOne, OxmlElement, RequiredAttribute,
    ZeroOrMore, ZeroOrOne
)


class CT_DLbl(BaseOxmlElement):
    """
    ``<c:dLbl>`` element specifying the properties of the data label for an
    individual data point.
    """
    _tag_seq = (
        'c:idx', 'c:layout', 'c:tx', 'c:numFmt', 'c:spPr', 'c:txPr',
        'c:dLblPos', 'c:showLegendKey', 'c:showVal', 'c:showCatName',
        'c:showSerName', 'c:showPercent', 'c:showBubbleSize', 'c:separator',
        'c:extLst',
    )
    idx = OneAndOnlyOne('c:idx')
    tx = ZeroOrOne('c:tx', successors=_tag_seq[3:])
    del _tag_seq

    def get_or_add_tx_rich(self):
        """
        Return the `c:tx[c:rich]` subtree, newly created if not present.
        """
        tx = self.get_or_add_tx()
        tx._remove_strRef()
        tx.get_or_add_rich()
        return tx

    @property
    def idx_val(self):
        """
        The integer value of the `val` attribute on the required `c:idx`
        child.
        """
        return self.idx.val

    @classmethod
    def new_dLbl(cls):
        """
        Return a newly created "loose" `c:dLbl` element containing its
        default subtree.
        """
        dLbl = OxmlElement('c:dLbl')
        idx = OxmlElement('c:idx')
        showLegendKey = OxmlElement('c:showLegendKey')
        showLegendKey.val = False
        dLbl.append(idx)
        dLbl.append(showLegendKey)
        return dLbl

    def remove_tx_rich(self):
        """
        Remove any `c:tx[c:rich]` child, or do nothing if not present.
        """
        matches = self.xpath('c:tx[c:rich]')
        if not matches:
            return
        tx = matches[0]
        self.remove(tx)


class CT_DLblPos(BaseOxmlElement):
    """
    ``<c:dLblPos>`` element specifying the positioning of a data label with
    respect to its data point.
    """
    val = RequiredAttribute('val', XL_DATA_LABEL_POSITION)


class CT_DLbls(BaseOxmlElement):
    """
    ``<c:dLbls>`` element specifying the properties of a set of data labels.
    """
    _tag_seq = (
        'c:dLbl', 'c:numFmt', 'c:spPr', 'c:txPr', 'c:dLblPos',
        'c:showLegendKey', 'c:showVal', 'c:showCatName', 'c:showSerName',
        'c:showPercent', 'c:showBubbleSize', 'c:separator',
        'c:showLeaderLines', 'c:leaderLines', 'c:extLst'
    )
    dLbl = ZeroOrMore('c:dLbl', successors=_tag_seq[1:])
    numFmt = ZeroOrOne('c:numFmt', successors=_tag_seq[2:])
    txPr = ZeroOrOne('c:txPr', successors=_tag_seq[4:])
    dLblPos = ZeroOrOne('c:dLblPos', successors=_tag_seq[5:])
    del _tag_seq

    _default_xml = (
        '<c:dLbls %s>\n'
        '  <c:showLegendKey val="0"/>\n'
        '  <c:showVal val="1"/>\n'
        '  <c:showCatName val="0"/>\n'
        '  <c:showSerName val="0"/>\n'
        '  <c:showPercent val="0"/>\n'
        '  <c:showBubbleSize val="0"/>\n'
        '</c:dLbls>' % nsdecls('c')
    )

    @property
    def defRPr(self):
        """
        ``<a:defRPr>`` great-great-grandchild element, added with its
        ancestors if not present.
        """
        txPr = self.get_or_add_txPr()
        defRPr = txPr.defRPr
        return defRPr

    def get_dLbl_for_point(self, idx):
        """
        Return the `c:dLbl` child representing the label for the data point
        at index *idx*.
        """
        matches = self.xpath('c:dLbl[c:idx[@val="%d"]]' % idx)
        if matches:
            return matches[0]
        return None

    def get_or_add_dLbl_for_point(self, idx):
        """
        Return the `c:dLbl` element representing the label of the point at
        index *idx*.
        """
        matches = self.xpath('c:dLbl[c:idx[@val="%d"]]' % idx)
        if matches:
            return matches[0]
        return self._insert_dLbl_in_sequence(idx)

    @classmethod
    def new_default(cls):
        """
        Return a new default ``<c:dLbls>`` element.
        """
        xml = cls._default_xml
        dLbls = parse_xml(xml)
        return dLbls

    def _insert_dLbl_in_sequence(self, idx):
        """
        Return a newly created `c:dLbl` element having `c:idx` child of *idx*
        and inserted in numeric sequence among the `c:dLbl` children of this
        element.
        """
        new_dLbl = self._new_dLbl()
        new_dLbl.idx.val = idx

        dLbl = None
        for dLbl in self.dLbl_lst:
            if dLbl.idx_val > idx:
                dLbl.addprevious(new_dLbl)
                return new_dLbl
        if dLbl is not None:
            dLbl.addnext(new_dLbl)
        else:
            self.insert(0, new_dLbl)
        return new_dLbl

    def _new_dLbl(self):
        return CT_DLbl.new_dLbl()

    def _new_txPr(self):
        return CT_TextBody.new_txPr()

"""Utilities for translating ORF detection
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import warnings

from collections import Counter
from collections import defaultdict

import sys
from .interval import Interval


class ORF:
    """Class for candidate ORF."""

    def __init__(self,
                 category,
                 transcript_id,
                 transcript_type,
                 gene_id,
                 gene_name,
                 gene_type,
                 chrom,
                 strand,
                 intervals,
                 seq='',
                 leader='',
                 trailer=''):
        self.category = category
        self.tid = transcript_id
        self.ttype = transcript_type
        self.gid = gene_id
        self.gname = gene_name
        self.gtype = gene_type
        self.chrom = chrom
        self.strand = strand
        self.intervals = sorted(intervals, key=lambda x: x.start)
        start = self.intervals[0].start
        end = self.intervals[-1].end
        self.oid = '{}_{}_{}_{}'.format(
            transcript_id, start, end,
            sum([x.end - x.start + 1 for x in self.intervals]))
        self.seq = seq
        self.leader = leader
        self.trailer = trailer

    @property
    def start_codon(self):
        if len(self.seq) < 3:
            return None
        return self.seq[:3]

    @classmethod
    def from_string(cls, line):
        """
        Parameters
        ----------
        line: string
              line for ribocop index file generated by prepare_orfs
        """
        if not line:
            print('annotation line cannot be empty')
            return None
        fields = line.split('\t')
        if len(fields) != 10:
            sys.exit('{}\n{}'.format(
                'Error: unexpected number of columns found for index file',
                'please run RiboCop prepare-orfs to regenerate'))
            return None
        oid = fields[0]
        category = fields[1]
        tid = fields[2]
        ttype = fields[3]
        gid = fields[4]
        gname = fields[5]
        gtype = fields[6]
        chrom = fields[7]
        strand = fields[8]
        coordinate = fields[9]
        intervals = []
        for group in coordinate.split(','):
            start, end = group.split('-')
            start = int(start)
            end = int(end)
            intervals.append(Interval(chrom, start, end, strand))
        # seq = fields[10]
        # leader = fields[11]
        # trailer = fields[12]
        return cls(category, tid, ttype, gid, gname, gtype, chrom, strand,
                   intervals)

    @classmethod
    def from_tracks(cls, tracks, category, seq='', leader='', trailer=''):
        """
        Parameters
        ----------
        tracks: list of GTFTrack
        """
        if not tracks:
            return None
        intervals = []
        tid = set()
        ttype = set()
        gid = set()
        gname = set()
        gtype = set()
        chrom = set()
        strand = set()
        for track in tracks:
            try:
                tid.add(track.transcript_id)
                ttype.add(track.transcript_type)
                gid.add(track.gene_id)
                gname.add(track.gene_name)
                gtype.add(track.gene_type)
                chrom.add(track.chrom)
                strand.add(track.strand)
                intervals.append(
                    Interval(track.chrom, track.start, track.end,
                             track.strand))
            except AttributeError:
                print('missing attribute {}:{}-{}'.format(
                    track.chrom, track.start, track.end))
                return None
        if (len(tid) != 1 or len(ttype) != 1 or len(gid) != 1
                or len(gname) != 1 or len(gtype) != 1 or len(chrom) != 1
                or len(strand) != 1):
            print('inconsistent tracks for one ORF')
            return None
        tid = list(tid)[0]
        ttype = list(ttype)[0]
        gid = list(gid)[0]
        gname = list(gname)[0]
        gtype = list(gtype)[0]
        chrom = list(chrom)[0]
        strand = list(strand)[0]
        return cls(category, tid, ttype, gid, gname, gtype, chrom, strand,
                   intervals, seq, leader, trailer)

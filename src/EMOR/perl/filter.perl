#!/usr/bin/perl

while (<>) {
  next if /^;;;/;
  chomp;
  s/(\tN )3(sg|pl)/$1$2/g;
  if (s/^(\S+)\s+//) {
    $w = $1;
    foreach $x (split(/\#/)) {
      print "$w\t$x\n";
    }
  }
}

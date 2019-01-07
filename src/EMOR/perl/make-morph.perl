#!/usr/bin/perl

while (<>) {
  print STDERR "\r$N" if ++$N % 1000 == 0;
  if (s/(<[^<>]+>)//) {
    $pos{$1} = 1;
  }
  while (s/(<[^<>]+>)//) {
    $tag{$1} = 1;
  }
}
print STDERR "\n";

$t1 = join('',sort keys %pos);
$t2 = join('',sort keys %tag);

print "ALPHABET = [\\!-ÿ] [$t1 $t2]:<>\n\n\$ANY\$ = .*\n\n";
print "\"lexicon\" || \$ANY\$\n";

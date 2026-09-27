```perl
#!/usr/bin/env perl

use strict;
use warnings;
use File::Find;
use File::Copy qw(copy);
use Digest::SHA qw(sha256_hex);
use Getopt::Long qw(GetOptions);

my $command = '';
my $path    = '.';
my $target  = '';
my $pattern = '';

GetOptions(
    'command=s' => \$command,
    'path=s'    => \$path,
    'target=s'  => \$target,
    'pattern=s' => \$pattern,
) or die usage();

sub usage {
    return <<'USAGE';
Game Engine Utility

Usage:
    perl util.pl --command list   --path assets
    perl util.pl --command find   --path assets --pattern "\.png$"
    perl util.pl --command hash   --path assets
    perl util.pl --command copy   --path assets --target backup

Commands:
    list    List all files under a directory
    find    Find files matching a regex
    hash    Print SHA-256 hashes of files
    copy    Copy files to a target directory

Options:
    --path      Source directory
    --target    Destination directory
    --pattern   Regular expression for find
USAGE
}

die usage() unless $command;

sub walk_files {
    my ($root, $callback) = @_;

    find(
        {
            wanted => sub {
                return unless -f $_;
                $callback->($File::Find::name);
            },
            no_chdir => 1,
        },
        $root
    );
}

if ($command eq 'list') {

    walk_files($path, sub {
        print "$_[0]\n";
    });

}
elsif ($command eq 'find') {

    die "Missing --pattern\n" unless $pattern;

    my $regex = eval { qr/$pattern/ };
    die "Invalid regex: $@\n" if $@;

    walk_files($path, sub {
        my ($file) = @_;

        print "$file\n" if $file =~ $regex;
    });

}
elsif ($command eq 'hash') {

    walk_files($path

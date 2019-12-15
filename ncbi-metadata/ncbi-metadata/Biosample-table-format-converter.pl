#!/usr/bin/perl
use strict;
&main;

sub main{
    my @data;
    &read(\@data);
    &showData(\@data);
}

sub read{
    my $result=$_[0];
    my %data;
    my $key;
    my $value;
    my $i=0;
    while(my $line=<>){
	$line=~s/[\r\n]//g;
#	print $line,"\n";
#	if($line=~/^Identifiers: /){
       if($line=~/^Identifiers/){
#	    print "  -- found header: $line --\n";
	    if(exists($data{"HEAD"})){
		%{$result->[$i++]}=%data;
	    }
	    undef(%data);
	    $data{"HEAD"}=$line;
	}elsif($line=~/^\s+\//){
	    ($key=$line)=~s/^\s+\/(.*?)=(.*)/$1/;
	    ($value=$line)=~s/^\s+\/(.*?)=(.*)/$2/;
#	    print "  == found data: $key => $value\n";
	    $data{$key}=$value;
	}
    }
    if(exists($data{"HEAD"})){
	%{$result->[$i++]}=%data;
    }
}

sub showData{ #(\@data)
    my $data=$_[0];
    my %keys;
    my $key;
    my @list;
    foreach my $line (@{$data}){
	foreach $key (keys %{$line}){
	    $keys{$key}=1;
	}
    }
    delete($keys{"HEAD"});
    @list=sort keys %keys;
    printf("\t%s\n", join("\t", @list));
    foreach my $line (@{$data}){
	print $line->{"HEAD"};
	foreach $key (@list){
	    if(exists($line->{$key})){
		$line->{$key}=~s/^\"(.*)\"$/$1/;
		print "\t".$line->{$key};
	    }else{
		print "\tN/A";
	    }
	}
	print "\n";
    }
}

=pod
sub showData{ #(\@header, \%data);
    my $header=$_[0];
    my $data=$_[1];
    print $data->{"HEAD"};
    foreach my $key (@{$header}){
	if(exists($data->{$key})){
	    $data->{$key}=~s/^\"(.*)\"$/$1/;
	    print "\t".$data->{$key};
	}else{
	    print "\tN/A";
	}
    }
    print "\n";
}
=cut

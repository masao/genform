#!/usr/local/bin/perl -wT
# -*-CPerl-*-
# $Id$

# Web 上で動的にフォームの設定情報を入力する

use strict;
use CGI qw/:cgi/;
use CGI::Carp 'fatalsToBrowser';
use HTML::Template;

$| = 1;

use lib ".";
require 'util.pl';

require 'default_conf.pl';
if (defined valid_dbname()) {
    require "$conf::DATADIR/". valid_dbname() ."/conf.pl"
	if -r "$conf::DATADIR/". valid_dbname() ."/conf.pl";
    require "$conf::DATADIR/". valid_dbname() ."/form.pl"
	if -r "$conf::DATADIR/". valid_dbname() ."/form.pl";
}

main();
sub main {
    print header("text/html; charset=EUC-JP");
    my $message = verify_status();

    if (defined valid_dbname()) {
	my $tmpl = HTML::Template->new('filename' => 'template/genform.tmpl');
	$tmpl->param('SCRIPT_NAME' => script_name(),
		     'DBNAME' => valid_dbname(),
		     'MESSAGE' => $message,
		     'TITLE' => $conf::TITLE,
		     'HOME_TITLE' => $conf::HOME_TITLE,
		     'HOME_URL' => $conf::HOME_URL,
		     'EMAIL' => $conf::EMAIL,
		     'NOTE' => $conf::NOTE,
		     'FORM' => param2form($conf::FORM));
	print $tmpl->output;
    } else {
	my $tmpl = HTML::Template->new('filename' => 'template/dblist.tmpl');
	$tmpl->param('TITLE' => '一覧',
		     'MESSAGE' => $message,
		     'DBINFO' => get_dbinfo());
	print $tmpl->output;
    }
}

sub get_dbinfo() {
    my $retstr = '';
    opendir(D, "$conf::DATADIR") || die "opendir fail: $conf::DATADIR: $!";
    my @dirs = grep { -d "$conf::DATADIR/$_" && /^\w+$/ } readdir(D);
    closedir(D);

    my $script_name = script_name();
    foreach my $db (@dirs) {
	next unless -r "$conf::DATADIR/$db/conf.pl" &&
	            -r "$conf::DATADIR/$db/form.pl";
	require "$db/conf.pl" if -r "$db/conf.pl";
	$retstr .= "<li><a href=\"$script_name/$db\">";
	$retstr .= CGI::escapeHTML(defined $conf::TITLE ? $conf::TITLE : $db);
	$retstr .= "</li>\n";
    }
    return $retstr;
}

# パラメータなどから、エラー状況などを確認する。
sub verify_status() {
    my $message = '';
    if (! -d $conf::DATADIR) {
	$message .= "<p class=\"error-message\">エラー: ディレクトリ <code>$conf::DATADIR</code> が存在しません。</p>\n";
    } elsif (! -w $conf::DATADIR) {
	$message .= "<p class=\"error-message\">エラー: ディレクトリ <code>$conf::DATADIR</code> に書きこみできません。</p>\n";
    }

    if (path_info()) {
	my $dbname = valid_dbname();
	$message .= "<p class=\"error-message\">エラー: 存在しないデータベースを指定しています。</p>" if not defined $dbname;

	unless (-r "$conf::DATADIR/$dbname/conf.pl" &&
		-r "$conf::DATADIR/$dbname/form.pl") {
	    $message .= "<p class=\"error-message\">エラー: データベースは設定中です。</p>"
	}
    }
    return $message;
}

sub tostr($) {
    my ($str) = (@_);
    if (defined $str) {
	$str =~ s/'/\\'/g;
	return "'$str'";
    } else {
	return "undef";
    }
}

muda($conf::TITLE, $conf::EMAIL, $conf::HOME_URL, $conf::HOME_TITLE,
     $conf::NOTE);

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
# 既存の設定内容で上書き
require "$conf::DATADIR/conf.pl" if -r "$conf::DATADIR/conf.pl";

my %FORM =
    ('new' => [
	       { -type => 'hidden',
		 -id => 'passwd' },
	       { -type => 'textfield',
		 -id => 'dbname',
		 -label => 'データベースID',
		 -description => '半角英数字のみで入力してください。',
		 -required => 1 },
	      ],
     'dbconfig' => [
		{ -type => 'fieldset',
		  -label => 'マシン固有の設定',
		  -value => [ { -id => 'nkf',
				-type => 'textfield',
				-label => 'nkf コマンド',
				-description => 'nkf コマンドの位置を指定します。',
				-value => "/usr/local/bin/nkf" },
			      { -id => 'sendmail',
				-type => 'textfield',
				-label => 'sendmail コマンド',
				-description => 'sendmail コマンドの位置を指定します。',
				-value => "/usr/lib/sendmail" } ] },
		 { -type => 'fieldset',
		   -label => '全般の設定',
		   -value => [ { -id => 'email',
				 -type => 'textfield',
				 -label => '担当者のメールアドレス' },
			       { -id => 'title',
				 -type => 'textfield',
				 -label => 'ページのタイトル' },
			       { -id => 'home_url',
				 -type => 'textfield',
				 -label => 'ホームページの URL',
				 -value => 'http://' },
			       { -id => 'home_title',
				 -type => 'textfield',
				 -label => 'ホームページのタイトル' },
			       { -id => 'note',
				 -type => 'textarea',
				 -label => 'フォームの先頭に書く注意事項（HTML）',
				 -rows => 4 } ] },
		 { -type => 'fieldset',
		   -label => 'システム機能の設定',
		   -value => [ { -id => 'datafile',
				 -type => 'textfield',
				 -label => '登録内容を記録するCSVファイル',
				 -description => '`chmod a+w $FILENAME`しておくこと。' },
			       { -id => 'use_mail',
				 -type => 'menu',
				 -label => 'メール通知機能を使う？',
				 -description => '使う場合は 1 にする。',
				 -value => [ "on", "off" ],
				 -default => "on" },
			       { -id => 'mail_subject',
				 -type => 'textfield',
				 -label => 'メール通知する場合の Subject',
				 -description => '非ASCIIは使えない' } ] },
		 ],
     'init' => [
		{ -type => 'passwd',
		  -id => 'passwd',
		  -label => "管理者パスワード",
		  -size => 50,
		  -description => '管理用タスクを実行するのに必要なパスワード（4文字以上の英数字）を設定してください。',
		  -required => 1,
		  -validate => sub {
		      my $val = shift;
		      if ($val =~ /^\w+$/ && length($val) >= 4) {
			  return 1;
		      } else {
			  return undef;
		      }
		  } }
	       ],
     'login' => [ { -type => 'passwd',
		    -id => 'passwd',
		    -label => "管理者パスワード" },
		  { -type => 'hidden',
		    -id => 'action',
		    -value => 'login' } ],
     );

main();
sub main {
    print header();
    my $message = verify_status();

    if (!length($message) && defined param('action')) {
	my $action = param('action');
	if ($action eq 'init') {
	    $message .= action_init();
	} elsif ($action eq 'login') {
	    $message .= action_login();
	} elsif ($action eq 'new') {
	    $message .= action_new();
	} elsif ($action eq 'dbconfig') {
	} else {
	    $message .= "<p class=\"error-message\">エラー: 不正なCGI引数です。 （<code>action=". CGI::escapeHTML($action). "</code>）</p>\n";
	}
    }

    if (! -r "$conf::DATADIR/.passwd") {
	my $tmpl = HTML::Template->new('filename' => 'template/init.tmpl');
	$tmpl->param('SCRIPT_NAME' => script_name(),
		     'TITLE' => '初期パスワード設定',
		     'MESSAGE' => $message,
		     'FORM_CONTROL' => param2form($FORM{'init'}));
	print $tmpl->output;
    } elsif (defined(my $db = has_valid_dbname()) && has_valid_passwd()) {
	my $tmpl = HTML::Template->new('filename' => 'template/dbconfig.tmpl');
	$tmpl->param('SCRIPT_NAME' => script_name(),
		     'DBNAME' => $db,
		     'TITLE' => "データベースの設定/編集: ". $db,
		     'MESSAGE' => $message,
		     'FORM_CONFIG' => param2form($FORM{'dbconfig'}));
	print $tmpl->output;
    } elsif (has_valid_passwd()) {
	my $tmpl = HTML::Template->new('filename' => 'template/main.tmpl');
	$tmpl->param('SCRIPT_NAME' => script_name(),
		     'TITLE' => 'メインメニュー',
		     'MESSAGE' => $message,
		     'DBINFO' => get_dbinfo(),
		     'FORM_NEW' => param2form($FORM{'new'}));
	print $tmpl->output;
    } else {
	my $tmpl = HTML::Template->new('filename' => 'template/login.tmpl');
	$tmpl->param('SCRIPT_NAME' => script_name(),
		     'TITLE' => 'ログイン',
		     'MESSAGE' => $message,
		     'FORM_CONTROL' => param2form($FORM{'login'}));
	print $tmpl->output;
    }
}

# path_info() が正当か検証し、正しければそのデータベース名を返す。
sub has_valid_dbname($) {
    my ($db) = path_info();
    return undef if !defined($db) || !length($db);
    if (-d "$conf::DATADIR$db") {
	return substr($db, 1);
    } else {
	return undef;
    }
}

sub get_dbinfo() {
    my $retstr = '';
    opendir(D, "$conf::DATADIR") || die "opendir fail: $conf::DATADIR: $!";
    my @dirs = grep { -d "$conf::DATADIR/$_" && /^\w+$/ } readdir(D);
    closedir(D);
    foreach my $db (@dirs) {
	$retstr .= "<tr><td>". CGI::escapeHTML($db) ."</td><td>";
	$retstr .= "<form method=\"POST\" action=\"". script_name() ."/";
	$retstr .= CGI::escapeHTML($db) ."\">";
	$retstr .= "<input type=\"hidden\" name=\"action\" value=\"dbconfig\">";
	$retstr .= "<input type=\"hidden\" name=\"passwd\" value=\"";
	$retstr .= CGI::escapeHTML(param('passwd')) ."\">";
	$retstr .= "<input type=\"submit\" value=\" 設定/編集 \">";
	$retstr .= "</form></td></tr>\n";
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

    my $action = param('action');
    $message .= validate_params($FORM{$action})
	if (defined $action && defined $FORM{$action});

    return $message;
}

sub action_init() {
    my $passwd = param('passwd');
    my $salt = join '', ('.', '/', 0..9, 'A'..'Z', 'a'..'z')[rand 64, rand 64];
    my $crypted_passwd = crypt($passwd, $salt);

    my $fh = util::fopen(">$conf::DATADIR/.passwd");
    print $fh $crypted_passwd;
    $fh->close;

    return "<p class=\"message\">パスワードの初期設定を完了しました。</p>\n";
}

sub action_login() {
    if (has_valid_passwd()) {
	return "<p class=\"message\">認証に成功しました。</p>"
    } else {
	return "<p class=\"error-message\">エラー: パスワードが違います。</p>"
    }
}

sub action_new() {
    my $dbname = util::untaint(param('dbname'), '\w+');
    my $dir = "$conf::DATADIR/$dbname";

    return "<p class=\"error-message\">エラー: データベース <strong>".
	   CGI::escapeHTML($dbname) ."</strong> は既に存在します。</p>"
		   if (-d $dir);

    mkdir($dir, 0777) || die "mkdir fail: $dir: $!";

    return "<p class=\"message\">データベース <strong>".
	   CGI::escapeHTML($dbname) ."</strong> の作成に成功しました。</p>"
}

# 必須項目のチェックを行う
sub validate_params(\@) {
    my ($parameter, $prefix) = @_;
    my $msg = '';
    my $i = 0;
    foreach my $entry (@{$parameter}) { # 必須項目のエラー処理
	my $id = $prefix;
	$id .= $i++ unless defined $id;
	$id = $$entry{-id} if defined $$entry{-id};

	if ($$entry{-type} eq 'fieldset') {
	    $msg .= validate_params($$entry{-value}, "$id.");
	} else {
	    if (defined($$entry{-required}) &&
		(!defined(param($id)) || !length(param($id)))) {
		$msg .= "<p class=\"error-message\">エラー: 「<strong>$$entry{-label}</strong>」は必須項目です。</p>\n";
	    }
	    if (defined($$entry{-validate}) &&
		defined(param($id)) && length(param($id))) {
		unless ($$entry{-validate}->(param($id))) {
		    $msg .= "<p class=\"error-message\">エラー: 「<strong>$$entry{-label}</strong>」の値 <strong>". CGI::escapeHTML(param($id)) ."</strong> は不正な形式です。</p>\n";
		}
	    }
	}
    }
    return $msg;
}

# CGI 引数 passwd を検証する
sub has_valid_passwd() {
    my $passwd = param('passwd');
    my $passwdfile = "$conf::DATADIR/.passwd";
    if (-r "$conf::DATADIR/.passwd" && defined $passwd) {
	my $cur_passwd = util::readfile($passwdfile);
	return 1 if (crypt($passwd, $cur_passwd) eq $cur_passwd);
    }
    return undef;
}

# フォームから受けとったパラメータを Perl 構文に変換して conf.pl に置く。
sub param2conf(@) {
    my (@parameter) = @_;
    my $str = '';
    foreach my $entry (@parameter) {
	$str .= '$'. uc($entry) .' = '. tostr(param($entry)) .";\n";
    }
    return $str;
}

# フォーム部品を設定に従って配置する
sub param2form(\@$) {
    my ($parameter, $prefix) = @_;
    my $retstr = '';
    my $i = 0;
    foreach my $entry (@$parameter) {
	my $id = $prefix;
	$id .= $i++ unless defined $id;
	$id = $$entry{-id} if defined $$entry{-id};

	if ($$entry{-type} eq 'hidden') {
	    $retstr .= "<input type=\"hidden\" name=\"$id\" value=\"";
	    if (defined param($id)) {
		$retstr .= CGI::escapeHTML(param($id));
	    } elsif (defined $$entry{-value}) {
		$retstr .= CGI::escapeHTML($$entry{-value});
	    }
	    $retstr .= "\">\n";
	    next;
	}

	$retstr .= "<tr><td>$$entry{-label}";
	$retstr .= " ※" if defined $$entry{-required};
	$retstr .= "</td><td>";

	if ($$entry{-type} eq 'fieldset') {
	    $retstr .= "<table>\n";
	    $retstr .= param2form($$entry{-value}, "$id.");
	    $retstr .= "</table>\n";
	} elsif ($$entry{-type} eq 'textfield') {
	    $retstr .= "<input type=\"text\" name=\"$id\" value=\"";
	    if (defined param($id)) {
		$retstr .= CGI::escapeHTML(param($id));
	    } elsif (defined $$entry{-value}) {
		$retstr .= CGI::escapeHTML($$entry{-value});
	    }
	    $retstr .= "\"";
	    $retstr .= " size=\"$$entry{-size}\"" if defined $$entry{-size};
	    $retstr .= ">";

	    if (defined $$entry{-repeatable}) {
		$retstr .= "<br><small>複数の項目を登録する場合は、コンマで区切って入れてください。<br>例: $conf::PARAM_LABELS{$entry}1,$conf::PARAM_LABELS{$entry}2,$conf::PARAM_LABELS{$entry}3</small>";
	    }
	} elsif ($$entry{-type} eq 'textarea') {
	    $retstr .= "<textarea name=\"$id\"";
	    $retstr .= " rows=\"$$entry{-rows}\"" if defined $$entry{-rows};
	    $retstr .= " cols=\"$$entry{-cols}\"" if defined $$entry{-cols};
	    $retstr .= ">";
	    if (defined param($id)) {
		$retstr .= CGI::escapeHTML(param($id));
	    } elsif (defined $$entry{-value}) {
		$retstr .= CGI::escapeHTML($$entry{-value});
	    }
	    $retstr .= "</textarea>";
	} elsif ($$entry{-type} eq 'passwd') {
	    $retstr .= "<input type=\"password\" name=\"$id\" value=\"\"";
	    $retstr .= " size=\"$$entry{-size}\"" if defined $$entry{-size};
	    $retstr .= ">";
	}
	if (defined $$entry{-description}) {
	    $retstr .= "<br><small>$$entry{-description}</small>";
	}
	$retstr .= "</td></tr>\n";
    }
    return $retstr;
}

sub tostr($) {
    my ($str) = (@_);
    if (defined $str) {
	return "\"$str\"";
    } else {
	return "undef";
    }
}

#!/usr/local/bin/perl -wT
# -*-CPerl-*-
# $Id$

# Web 上で動的にフォームの設定情報を入力する

use strict;
use CGI qw/:cgi/;
use CGI::Carp 'fatalsToBrowser';
use HTML::Template;
use Data::Dumper;

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
		    { -type => 'hidden',
		      -id => 'passwd' },
		    { -id => 'email',
		      -type => 'textfield',
		      -label => '担当者のメールアドレス',
		      -value => $conf::EMAIL },
		    { -id => 'title',
		      -type => 'textfield',
		      -label => 'タイトル',
		      -value => $conf::TITLE },
		    { -id => 'home_url',
		      -type => 'textfield',
		      -label => 'ホームページの URL',
		      -value => $conf::HOME_URL },
		    { -id => 'home_title',
		      -type => 'textfield',
		      -label => 'ホームページのタイトル',
		      -value => $conf::HOME_TITLE },
		    { -id => 'note',
		      -type => 'textarea',
		      -label => '入力フォームの先頭に書く注意事項',
		      -value => $conf::NOTE,
		      -rows => 4 },
		   ],

     'addfield' => [
		    { -type => 'hidden',
		      -id => 'passwd' },
		    { -id => '-label',
		      -type => 'textfield',
		      -label => 'フィールド名',
		      -size => 50,
		      -required => 1 },
		    { -id => '-type',
		      -type => 'radio',
		      -label => 'フィールド種別',
		      -required => 1,
		      -value => [
				 { -id => 'textfield',
				   -label => '一行入力<br>' },
				 { -id => 'textarea',
				   -label => '複数行入力<br>' },
				 { -id => 'checkbox',
				   -label => 'チェックボックス<br>' },
				 { -id => 'radio',
				   -label => 'ラジオボタン<br>' },
				 { -id => 'menu',
				   -label => 'スクロールメニュー<br>' },
				 { -id => 'file',
				   -label => 'ファイル・アップロード<br>' },
				 { -id => 'password',
				   -label => 'パスワード入力<br>' },
				] },
		   ],

     'init' => [
		{ -type => 'password',
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

     'login' => [ { -type => 'password',
		    -id => 'passwd',
		    -label => "管理者パスワード",
		    -size => 50 }
		],
    );

main();
sub main {
    print header("text/html; charset=EUC-JP");
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
	    $message .= action_dbconfig();
	} elsif ($action eq 'addfield') {
	    $message .= action_addfield();
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
    } elsif (defined(my $db = valid_dbname()) && has_valid_passwd()) {
	my $tmpl = HTML::Template->new('filename' => 'template/dbconfig.tmpl');
	$tmpl->param('SCRIPT_NAME' => script_name(),
		     'DBNAME' => $db,
		     'TITLE' => "データベースの設定/編集: ". $db,
		     'MESSAGE' => $message,
		     'FORM_INFO' => get_forminfo(),
		     'FORM_ADDFIELD' => param2form($FORM{'addfield'}),
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

sub get_dbinfo() {
    my $retstr = '';
    opendir(D, "$conf::DATADIR") || die "opendir fail: $conf::DATADIR: $!";
    my @dirs = grep { -d "$conf::DATADIR/$_" && /^\w+$/ } readdir(D);
    closedir(D);
    foreach my $db (@dirs) {
	$retstr .= "<tr><td>". CGI::escapeHTML($db) ."</td><td>";
	$retstr .= "<form method=\"POST\" action=\"". script_name() ."/";
	$retstr .= CGI::escapeHTML($db) ."\">";
	$retstr .= "<input type=\"hidden\" name=\"passwd\" value=\"";
	$retstr .= CGI::escapeHTML(param('passwd')) ."\">";
	$retstr .= "<input type=\"submit\" value=\" 設定/編集 \">";
	$retstr .= "</form></td></tr>\n";
    }
    return $retstr;
}

sub get_forminfo() {
    my $retstr = '';
    my $dbname = valid_dbname();
    if (defined $conf::FORM) {
	my $i = 0;
	foreach my $entry (@$conf::FORM) {
	    my $id = $i++;
	    $id = $$entry{-id} if defined $$entry{-id};

	    $retstr .= "<tr><td>". CGI::escapeHTML($$entry{-label}) ."</td><td>";
	    $retstr .= "<form method=\"POST\" action=\"". script_name() ."/";
	    $retstr .= CGI::escapeHTML($dbname) ."\">";
	    $retstr .= "<input type=\"hidden\" name=\"passwd\" value=\"";
	    $retstr .= CGI::escapeHTML(param('passwd')) ."\">";
	    $retstr .= "<input type=\"hidden\" name=\"action\" value=\"editform\">";
	    $retstr .= "<input type=\"hidden\" name=\"id\" value=\"$id\">";
	    $retstr .= "<input type=\"submit\" value=\" 設定/編集 \">";
	    $retstr .= "</form></td></tr>\n";
	}
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

    my $fh = fopen(">$conf::DATADIR/.passwd");
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
    my $dbname = untaint(param('dbname'), '\w+');
    my $dir = "$conf::DATADIR/$dbname";

    return "<p class=\"error-message\">エラー: データベース <strong>".
	   CGI::escapeHTML($dbname) ."</strong> は既に存在します。</p>"
		   if (-d $dir);

    mkdir($dir, 0777) || die "mkdir fail: $dir: $!";

    return "<p class=\"message\">データベース <strong>".
	   CGI::escapeHTML($dbname) ."</strong> の作成に成功しました。</p>"
}

sub action_dbconfig() {
    my $dbname = valid_dbname();
    my $conf_str = param2conf('title', 'email', 'home_url', 'home_title',
			      'note');
    my $fh = fopen(">$conf::DATADIR/$dbname/conf.pl");
    print $fh "package conf;\n";
    print $fh $conf_str;
    print $fh "1;\n";
    return "<p class=\"message\">データベース <strong>".
	   CGI::escapeHTML($dbname) ."</strong> の設定を完了しました。</p>";
}

sub action_addfield() {
    my $dbname = valid_dbname();
    my %field = ();
    $field{-label} = param('-label');
    $field{-type} = param('-type');
    if (defined $conf::FORM) {
	push @{$conf::FORM}, \%field;
    } else {
	$conf::FORM = [ \%field ];
    }
    my $dumper = Data::Dumper->new([ $conf::FORM ], [ qw/FORM/ ]);
    my $fh = fopen(">$conf::DATADIR/$dbname/form.pl");
    print $fh "package conf;\n";
    print $fh $dumper->Dump();
    print $fh "1;\n";
    return "<p class=\"message\">フィールド「<strong>".
	   CGI::escapeHTML(param('-label')) ."</strong>」を追加しました。</p>";
}

# CGI 引数 passwd を検証する
sub has_valid_passwd() {
    my $passwd = param('passwd');
    my $passwdfile = "$conf::DATADIR/.passwd";
    if (-r "$conf::DATADIR/.passwd" && defined $passwd) {
	my $cur_passwd = readfile($passwdfile);
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

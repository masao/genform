#!/usr/local/bin/perl -wT
# -*-CPerl-*-
# $Id$

# Web ���ưŪ�˥ե�����������������Ϥ���

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
		 -label => '�ǡ����١���ID',
		 -description => 'Ⱦ�ѱѿ����Τߤ����Ϥ��Ƥ���������',
		 -required => 1 },
	      ],

     'dbconfig' => [
		    { -type => 'hidden',
		      -id => 'passwd' },
		    { -id => 'email',
		      -type => 'textfield',
		      -label => 'ô���ԤΥ᡼�륢�ɥ쥹',
		      -value => $conf::EMAIL },
		    { -id => 'title',
		      -type => 'textfield',
		      -label => '�����ȥ�',
		      -value => $conf::TITLE },
		    { -id => 'home_url',
		      -type => 'textfield',
		      -label => '�ۡ���ڡ����� URL',
		      -value => $conf::HOME_URL },
		    { -id => 'home_title',
		      -type => 'textfield',
		      -label => '�ۡ���ڡ����Υ����ȥ�',
		      -value => $conf::HOME_TITLE },
		    { -id => 'note',
		      -type => 'textarea',
		      -label => '���ϥե��������Ƭ�˽���ջ���',
		      -value => $conf::NOTE,
		      -rows => 4 },
		   ],

     'addfield' => [
		    { -type => 'hidden',
		      -id => 'passwd' },
		    { -id => '-label',
		      -type => 'textfield',
		      -label => '�ե������̾',
		      -size => 50,
		      -required => 1 },
		    { -id => '-type',
		      -type => 'radio',
		      -label => '�ե�����ɼ���',
		      -required => 1,
		      -value => [
				 { -id => 'textfield',
				   -label => '�������<br>' },
				 { -id => 'textarea',
				   -label => 'ʣ��������<br>' },
				 { -id => 'checkbox',
				   -label => '�����å��ܥå���<br>' },
				 { -id => 'radio',
				   -label => '�饸���ܥ���<br>' },
				 { -id => 'menu',
				   -label => '���������˥塼<br>' },
				 { -id => 'file',
				   -label => '�ե����롦���åץ���<br>' },
				 { -id => 'password',
				   -label => '�ѥ��������<br>' },
				] },
		   ],

     'init' => [
		{ -type => 'password',
		  -id => 'passwd',
		  -label => "�����ԥѥ����",
		  -size => 50,
		  -description => '�����ѥ�������¹Ԥ���Τ�ɬ�פʥѥ���ɡ�4ʸ���ʾ�αѿ����ˤ����ꤷ�Ƥ���������',
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
		    -label => "�����ԥѥ����",
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
	    $message .= "<p class=\"error-message\">���顼: ������CGI�����Ǥ��� ��<code>action=". CGI::escapeHTML($action). "</code>��</p>\n";
	}
    }

    if (! -r "$conf::DATADIR/.passwd") {
	my $tmpl = HTML::Template->new('filename' => 'template/init.tmpl');
	$tmpl->param('SCRIPT_NAME' => script_name(),
		     'TITLE' => '����ѥ��������',
		     'MESSAGE' => $message,
		     'FORM_CONTROL' => param2form($FORM{'init'}));
	print $tmpl->output;
    } elsif (defined(my $db = valid_dbname()) && has_valid_passwd()) {
	my $tmpl = HTML::Template->new('filename' => 'template/dbconfig.tmpl');
	$tmpl->param('SCRIPT_NAME' => script_name(),
		     'DBNAME' => $db,
		     'TITLE' => "�ǡ����١���������/�Խ�: ". $db,
		     'MESSAGE' => $message,
		     'FORM_INFO' => get_forminfo(),
		     'FORM_ADDFIELD' => param2form($FORM{'addfield'}),
		     'FORM_CONFIG' => param2form($FORM{'dbconfig'}));
	print $tmpl->output;
    } elsif (has_valid_passwd()) {
	my $tmpl = HTML::Template->new('filename' => 'template/main.tmpl');
	$tmpl->param('SCRIPT_NAME' => script_name(),
		     'TITLE' => '�ᥤ���˥塼',
		     'MESSAGE' => $message,
		     'DBINFO' => get_dbinfo(),
		     'FORM_NEW' => param2form($FORM{'new'}));
	print $tmpl->output;
    } else {
	my $tmpl = HTML::Template->new('filename' => 'template/login.tmpl');
	$tmpl->param('SCRIPT_NAME' => script_name(),
		     'TITLE' => '������',
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
	$retstr .= "<input type=\"submit\" value=\" ����/�Խ� \">";
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
	    $retstr .= "<input type=\"submit\" value=\" ����/�Խ� \">";
	    $retstr .= "</form></td></tr>\n";
	}
    }
    return $retstr;
}

# �ѥ�᡼���ʤɤ��顢���顼�����ʤɤ��ǧ���롣
sub verify_status() {
    my $message = '';
    if (! -d $conf::DATADIR) {
	$message .= "<p class=\"error-message\">���顼: �ǥ��쥯�ȥ� <code>$conf::DATADIR</code> ��¸�ߤ��ޤ���</p>\n";
    } elsif (! -w $conf::DATADIR) {
	$message .= "<p class=\"error-message\">���顼: �ǥ��쥯�ȥ� <code>$conf::DATADIR</code> �˽񤭤��ߤǤ��ޤ���</p>\n";
    }

    if (path_info()) {
	my $dbname = valid_dbname();
	$message .= "<p class=\"error-message\">���顼: ¸�ߤ��ʤ��ǡ����١�������ꤷ�Ƥ��ޤ���</p>" if not defined $dbname;
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

    return "<p class=\"message\">�ѥ���ɤν�������λ���ޤ�����</p>\n";
}

sub action_login() {
    if (has_valid_passwd()) {
	return "<p class=\"message\">ǧ�ڤ��������ޤ�����</p>"
    } else {
	return "<p class=\"error-message\">���顼: �ѥ���ɤ��㤤�ޤ���</p>"
    }
}

sub action_new() {
    my $dbname = untaint(param('dbname'), '\w+');
    my $dir = "$conf::DATADIR/$dbname";

    return "<p class=\"error-message\">���顼: �ǡ����١��� <strong>".
	   CGI::escapeHTML($dbname) ."</strong> �ϴ���¸�ߤ��ޤ���</p>"
		   if (-d $dir);

    mkdir($dir, 0777) || die "mkdir fail: $dir: $!";

    return "<p class=\"message\">�ǡ����١��� <strong>".
	   CGI::escapeHTML($dbname) ."</strong> �κ������������ޤ�����</p>"
}

sub action_dbconfig() {
    my $dbname = valid_dbname();
    my $conf_str = param2conf('title', 'email', 'home_url', 'home_title',
			      'note');
    my $fh = fopen(">$conf::DATADIR/$dbname/conf.pl");
    print $fh "package conf;\n";
    print $fh $conf_str;
    print $fh "1;\n";
    return "<p class=\"message\">�ǡ����١��� <strong>".
	   CGI::escapeHTML($dbname) ."</strong> �������λ���ޤ�����</p>";
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
    return "<p class=\"message\">�ե�����ɡ�<strong>".
	   CGI::escapeHTML(param('-label')) ."</strong>�פ��ɲä��ޤ�����</p>";
}

# CGI ���� passwd �򸡾ڤ���
sub has_valid_passwd() {
    my $passwd = param('passwd');
    my $passwdfile = "$conf::DATADIR/.passwd";
    if (-r "$conf::DATADIR/.passwd" && defined $passwd) {
	my $cur_passwd = readfile($passwdfile);
	return 1 if (crypt($passwd, $cur_passwd) eq $cur_passwd);
    }
    return undef;
}

# �ե����फ������Ȥä��ѥ�᡼���� Perl ��ʸ���Ѵ����� conf.pl ���֤���
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

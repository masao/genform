#!/usr/local/bin/perl -wT
# -*-CPerl-*-
# $Id$

# Web ���ưŪ�˥ե�����������������Ϥ���

use strict;
use CGI qw/:cgi/;
use CGI::Carp 'fatalsToBrowser';
use HTML::Template;

$| = 1;

use lib ".";
require 'util.pl';

require 'default_conf.pl';
# ��¸���������ƤǾ��
require "$conf::DATADIR/conf.pl" if -r "$conf::DATADIR/conf.pl";

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
		{ -type => 'fieldset',
		  -label => '�ޥ����ͭ������',
		  -value => [ { -id => 'nkf',
				-type => 'textfield',
				-label => 'nkf ���ޥ��',
				-description => 'nkf ���ޥ�ɤΰ��֤���ꤷ�ޤ���',
				-value => "/usr/local/bin/nkf" },
			      { -id => 'sendmail',
				-type => 'textfield',
				-label => 'sendmail ���ޥ��',
				-description => 'sendmail ���ޥ�ɤΰ��֤���ꤷ�ޤ���',
				-value => "/usr/lib/sendmail" } ] },
		 { -type => 'fieldset',
		   -label => '���̤�����',
		   -value => [ { -id => 'email',
				 -type => 'textfield',
				 -label => 'ô���ԤΥ᡼�륢�ɥ쥹' },
			       { -id => 'title',
				 -type => 'textfield',
				 -label => '�ڡ����Υ����ȥ�' },
			       { -id => 'home_url',
				 -type => 'textfield',
				 -label => '�ۡ���ڡ����� URL',
				 -value => 'http://' },
			       { -id => 'home_title',
				 -type => 'textfield',
				 -label => '�ۡ���ڡ����Υ����ȥ�' },
			       { -id => 'note',
				 -type => 'textarea',
				 -label => '�ե��������Ƭ�˽���ջ����HTML��',
				 -rows => 4 } ] },
		 { -type => 'fieldset',
		   -label => '�����ƥൡǽ������',
		   -value => [ { -id => 'datafile',
				 -type => 'textfield',
				 -label => '��Ͽ���Ƥ�Ͽ����CSV�ե�����',
				 -description => '`chmod a+w $FILENAME`���Ƥ������ȡ�' },
			       { -id => 'use_mail',
				 -type => 'menu',
				 -label => '�᡼�����ε�ǽ��Ȥ���',
				 -description => '�Ȥ����� 1 �ˤ��롣',
				 -value => [ "on", "off" ],
				 -default => "on" },
			       { -id => 'mail_subject',
				 -type => 'textfield',
				 -label => '�᡼�����Τ������ Subject',
				 -description => '��ASCII�ϻȤ��ʤ�' } ] },
		 ],
     'init' => [
		{ -type => 'passwd',
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
     'login' => [ { -type => 'passwd',
		    -id => 'passwd',
		    -label => "�����ԥѥ����" },
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
    } elsif (defined(my $db = has_valid_dbname()) && has_valid_passwd()) {
	my $tmpl = HTML::Template->new('filename' => 'template/dbconfig.tmpl');
	$tmpl->param('SCRIPT_NAME' => script_name(),
		     'DBNAME' => $db,
		     'TITLE' => "�ǡ����١���������/�Խ�: ". $db,
		     'MESSAGE' => $message,
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

# path_info() �����������ڤ�����������Ф��Υǡ����١���̾���֤���
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
	$retstr .= "<input type=\"submit\" value=\" ����/�Խ� \">";
	$retstr .= "</form></td></tr>\n";
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
    my $dbname = util::untaint(param('dbname'), '\w+');
    my $dir = "$conf::DATADIR/$dbname";

    return "<p class=\"error-message\">���顼: �ǡ����١��� <strong>".
	   CGI::escapeHTML($dbname) ."</strong> �ϴ���¸�ߤ��ޤ���</p>"
		   if (-d $dir);

    mkdir($dir, 0777) || die "mkdir fail: $dir: $!";

    return "<p class=\"message\">�ǡ����١��� <strong>".
	   CGI::escapeHTML($dbname) ."</strong> �κ������������ޤ�����</p>"
}

# ɬ�ܹ��ܤΥ����å���Ԥ�
sub validate_params(\@) {
    my ($parameter, $prefix) = @_;
    my $msg = '';
    my $i = 0;
    foreach my $entry (@{$parameter}) { # ɬ�ܹ��ܤΥ��顼����
	my $id = $prefix;
	$id .= $i++ unless defined $id;
	$id = $$entry{-id} if defined $$entry{-id};

	if ($$entry{-type} eq 'fieldset') {
	    $msg .= validate_params($$entry{-value}, "$id.");
	} else {
	    if (defined($$entry{-required}) &&
		(!defined(param($id)) || !length(param($id)))) {
		$msg .= "<p class=\"error-message\">���顼: ��<strong>$$entry{-label}</strong>�פ�ɬ�ܹ��ܤǤ���</p>\n";
	    }
	    if (defined($$entry{-validate}) &&
		defined(param($id)) && length(param($id))) {
		unless ($$entry{-validate}->(param($id))) {
		    $msg .= "<p class=\"error-message\">���顼: ��<strong>$$entry{-label}</strong>�פ��� <strong>". CGI::escapeHTML(param($id)) ."</strong> �������ʷ����Ǥ���</p>\n";
		}
	    }
	}
    }
    return $msg;
}

# CGI ���� passwd �򸡾ڤ���
sub has_valid_passwd() {
    my $passwd = param('passwd');
    my $passwdfile = "$conf::DATADIR/.passwd";
    if (-r "$conf::DATADIR/.passwd" && defined $passwd) {
	my $cur_passwd = util::readfile($passwdfile);
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

# �ե��������ʤ�����˽��ä����֤���
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
	$retstr .= " ��" if defined $$entry{-required};
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
		$retstr .= "<br><small>ʣ���ι��ܤ���Ͽ������ϡ�����ޤǶ��ڤä�����Ƥ���������<br>��: $conf::PARAM_LABELS{$entry}1,$conf::PARAM_LABELS{$entry}2,$conf::PARAM_LABELS{$entry}3</small>";
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

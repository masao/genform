# -*- CPerl -*-
# $Id$

use strict;
use IO::File;

# 汚染されている変数をキレイにする。（CGI::Untaint のローカル実装）
sub untaint {
    my ($tainted, $pattern, $default) = @_;
    # print "\$tainted: $tainted\t\$pattern: $pattern\t\$default:$default\n";
    return $default if !defined $tainted;

    if ($tainted =~ /^($pattern)$/) {
        # print "matched.\n";
        return $1;
    } else {
        return $default;
    }
}

# 必須項目のチェックを行う
sub validate_params(\@$) {
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
	} elsif ($$entry{-type} eq 'radio') {
	    my $subid = 0;
	    foreach my $val (@{$$entry{-value}}) {
		my $myvalue = $$val{-id} || "$id.$subid";
		$retstr .= "<input type=\"radio\" name=\"$id\" value=\"$myvalue\"";
		if (defined(param($id)) && param($id) eq $myvalue) {
		    $retstr .= " checked";
		}
		$retstr .= ">";
		if (defined $$entry{-label}) {
		    $retstr .= $$val{-label}
		} else {
		    $retstr .= $myvalue;
		}
		$retstr .= "\n";
		$subid++;
	    }
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

# path_info() が正当か検証し、正しければそのデータベース名を返す。
sub valid_dbname() {
    my $dbname = untaint(path_info(), '/\w+');

    return undef if !defined($dbname) || !length($dbname);
    if (-d "$conf::DATADIR$dbname") {
	return substr($dbname, 1);
    } else {
	return undef;
    }
}

sub write_csv($@) {
    my ($fname, @values) = @_;
    my $fh = fopen(">>$fname");
    my @tmp = ();
    foreach my $entry (@values) {
	$entry =~ s/(["'])/\\$1/g;
	$entry = "\"$entry\"" if $entry =~ /[,\n\r]/;
	$entry =~ s/[\r\n]+/<br>/g;
	push @tmp, $entry;
    }
    print $fh join(',', @tmp), "\n";
}

sub send_mail($$$$$) {
    my ($from, $to, $subject, $name, $msg) = @_;
    my $fh = fopen("| $conf::NKF -j | $conf::SENDMAIL -oi -t -f $from");
    print $fh <<EOF;
From: $from
Subject: $subject
To: $to

 $name 様

$msg
EOF
}

sub html2txt {
    my ($html) = @_;
    my $tmpfile = "/tmp/.html2txt.$$";
    my $fh = fopen("|/usr/local/bin/w3m -dump -cols 78 -T text/html > $tmpfile");
    print $fh $html;
    $fh->close();
    my $result = readfile($tmpfile);
    unlink($tmpfile);
    return $result;
}

# HTMLの実体参照を行なう。
sub escape_html($) {
    my ($str) = @_;
    return undef if not defined $str;
    $str =~ s/&/&amp;/g;
    $str =~ s/</&lt;/g;
    $str =~ s/>/&gt;/g;
    $str =~ s/"/&quot;/go;
    return $str;
}

# 効率よくファイルの中身を読み込む。
sub readfile ($) {
    my ($fname) = @_;
    my $fh = fopen($fname);
    my $cont = '';
    my $size = -s $fh;
    read $fh, $cont, $size;
    $fh->close;
    return $cont;
}

sub fopen($) {
    my ($fname) = @_;
    my $fh = new IO::File;
    $fh->open($fname) || die "fopen: $fname: $!";
    return $fh;
}

# For avoiding "used only once: possible typo at ..." warnings.
sub muda {}
1;

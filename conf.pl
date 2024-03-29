#!/usr/local/bin/perl -w
# $Id$

package conf;

### 全般の設定

# 担当者のメールアドレス
$FROM = 'hasegawa@ulis.ac.jp';

# ページのタイトル
$TITLE = '数値解析シンポジウムメール案内登録';

# ホームページの URL
$HOME_URL = 'http://phase.hpcc.jp/nas/';

# ホームページのタイトル
$HOME_TITLE = '第31回数値解析シンポジウム (NAS2002)';

# フォームの先頭に書く注意事項（HTML）
$NOTE = <<EOF;
<p>
次からメールによる案内をご希望の方はご登録ください。
参加申し込みではありません。
</p>
EOF

# 登録内容を記録するCSVファイル: `chmod a+w $FILENAME`しておくこと。
$FILENAME = "annai.csv";

# 登録内容を記録するディレクトリ名: `chmod a+w $DATADIR`しておくこと。
$DATADIR = 'data';

# メール通知機能を使う？: 使う場合は 1 にする。
$USE_MAIL = 0;

  # メール通知する場合の Subject: （非ASCIIは使えない）
  $SUBJECT = 'NAS2002 registration';

### HTML の <form> 部品の定義

# フォーム部品のラベル（名前）
%PARAM_LABELS = ('name' => '名前',
		 'post' => '所属',
		 'e-mail' => 'E-mail',# メール通知する場合は必要（宛先）
		 'note' => '通信',
		 'date' => '登録日時',
		 'contact' => '連絡先',
		 'contact_name' => '名称',
		 'address' => '住所',
		 'phone' => '電話',
		 'keyword' => 'キーワード',
		);

# フォーム部品の表示順序、CVSファイルへの登録順も兼ねる
@PARAMETERS = ('name', 'post', 'e-mail', 'note', 'date', 'contact', 'keyword');

# フォーム部品のうち、必須入力項目のもの
# （「e-mail」の場合はメールアドレスの簡易チェックも行う）
%REQ_PARAMETERS = ('name' => 1, 'e-mail' => 1);

# フォーム部品の種類: textfield, textarea, radio, etc.
#
# 「external」は登録時に動的に情報を追加したい場合に用いる。
#
%PARAM_TYPES = ('name' => 'textfield:40', 'post' => 'textfield:40',
		'e-mail' => 'textfield:40', 'note' => 'textarea:4:50',
		'date' => 'external:scalar localtime()',
		'contact' => 'nest:contact_name:address:phone',
		'contact_name' => 'textfield',
		'address' => 'textfield',
		'phone' => 'textfield',
		'keyword' => 'textfield:50',
	       );

# repeatable な入力項目
%PARAM_REPEATABLES = ('keyword' => 1);

### HTMLの表現

# 処理終了時のメッセージ（HTML）の先頭部分
$REPORT_HEADER = <<EOF;
<p>
数値解析シンポジウムへの案内申し込みありがとうございます。
</p>
<p>
登録内容は以下の通りです。<br>
お問合せは <a href="mailto:$FROM">$FROM</a> までお願いいたします。
</p>
<p>
[登録内容]
</p>
<table border="2">
EOF

# 処理終了時のメッセージの最後の部分
$REPORT_FOOTER = <<EOF;
</table>
EOF

# HTMLの先頭部分
$HTML_HEADER = <<EOF;
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"
	"http://www.w3.org/TR/html4/loose.dtd">
<html lang="ja">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=EUC-JP">
<title>$TITLE</title>
</head>
<body>
<center>
<h1>$TITLE</h1>
EOF

# HTMLの最後の部分
$HTML_FOOTER = <<EOF;
</center>
<hr>
<a href="$HOME_URL">$HOME_TITLE</a>
</body>
</html>
EOF

### 設定おわり
1;

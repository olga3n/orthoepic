#!/usr/bin/env perl

# Dependencies

# 	festival TTS
#		http://www.festvox.org/festival/
# 	or espeak

# -----------------------------------------------------------------------------

use strict;

my $CLIENT_PORT = 12345;

use IO::Socket;

my $tts = '';

`festival --version`;
if (!$?) { $tts = 'festival'; }

if ($tts eq '') { 
	`espeak --version`;
	if (!$?) { $tts = 'espeak'; } 
}

while (1) {

	my $client = IO::Socket::INET->new( 
		PeerHost => '127.0.0.1',
		PeerPort => $CLIENT_PORT,
		Proto => 'tcp',
	);

	if ($client) {

		print $client "2\n";

		my $exit = 0;
		my $text = '';

		while (<$client>) {
			$text .= $_;
			$exit ++;
			last if $exit == 4;
		}

		print $text."\n\n";

		if($tts eq 'festival')
		{
			`echo "$text" | festival --tts --language russian`;
		}
		elsif ($tts eq 'espeak')
		{
			`espeak -v ru -g 8 -a 80 "$text"`;
		}
		else
		{
			sleep 4;
		}

		print $client "done\n";

		$client->close();
	}
}

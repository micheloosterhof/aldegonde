from aldegonde.algorithm import masc, pasc

ABC = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def test_vigenere() -> None:
    key = "LEMON"
    plaintext = "ATTACKATDAWN"
    ciphertext = "LXFOPVEFRNHR"
    assert tuple(ciphertext) == pasc.pasc_encrypt(plaintext, key, pasc.vigenere_tr(ABC))
    assert tuple(plaintext) == pasc.pasc_decrypt(ciphertext, key, pasc.vigenere_tr(ABC))


def test_beaufort() -> None:
    key = "FORTIFICATION"
    plaintext = "DEFENDTHEEASTWALLOFTHECASTLE"
    ciphertext = "CKMPVCPVWPIWUJOGIUAPVWRIWUUK"
    assert tuple(ciphertext) == pasc.pasc_encrypt(plaintext, key, pasc.beaufort_tr(ABC))
    assert tuple(plaintext) == pasc.pasc_decrypt(ciphertext, key, pasc.beaufort_tr(ABC))


def test_variantbeaufort() -> None:
    key = "CIPHER"
    plaintext = "HONESTYISTHEBESTPOLICY"
    ciphertext = "FGYXOCWADMDNZWDMLXJANR"
    assert tuple(ciphertext) == pasc.pasc_encrypt(
        plaintext, key, pasc.variantbeaufort_tr(ABC)
    )
    assert tuple(plaintext) == pasc.pasc_decrypt(
        ciphertext, key, pasc.variantbeaufort_tr(ABC)
    )


def test_quagmire1() -> None:
    """Is this quagmire1?."""
    return
    # alphabet = masc.keywordkey("ABCDEFGHIJKLMNOPQRSTUVWXYZ", "PAULBRANDT")
    # key = "BRANDT"
    # tr = pasc.quagmire1_tr(alphabet)
    # pasc.print_tr(tr)
    # plaintext = "DONTLETANYONETELLYOUTHESKYISTHELIMITWHENTHEREAREFOOTPRINTSONTHEMOON"
    # ciphertext = "HIFUFCIRFKUYKYJPFQSSHZMMQONGKFKTNDQAWDJSKFKVJNHCLIRUCXOWHGUYIDJDUKG"
    # assert tuple(ciphertext) == pasc.pasc_encrypt(
    #    plaintext, key, pasc.quagmire1_tr(alphabet)
    # )
    # assert tuple(plaintext) == pasc.pasc_decrypt(
    #    ciphertext, key, pasc.quagmire1_tr(alphabet)
    # )


def test_quagmire3() -> None:
    """ """
    alphabet = masc.keywordkey("ABCDEFGHIJKLMNOPQRSTUVWXYZ", "PAULBRANDT")
    key = "BRANDT"
    plaintext = "DONTLETANYONETELLYOUTHESKYISTHELIMITWHENTHEREAREFOOTPRINTSONTHEMOON"
    ciphertext = "FXDIEOGNDBZIIHFCENWDCQMUSLJPJVITJXVKPOFGJVIEFDGOJXQIDHOFCPZIGOFXZPE"
    assert tuple(ciphertext) == pasc.pasc_encrypt(
        plaintext, key, pasc.quagmire3_tr(alphabet)
    )
    assert tuple(plaintext) == pasc.pasc_decrypt(
        ciphertext, key, pasc.quagmire3_tr(alphabet)
    )


def test_quagmire3_kryptos1() -> None:
    """K1."""
    alphabet = masc.keywordkey("ABCDEFGHIJKLMNOPQRSTUVWXYZ", "KRYPTOS")
    key = "PALIMPSEST"
    ciphertext = "EMUFPHZLRFAXYUSDJKZLDKRNSHGNFIVJYQTQUXQBQVYUVLLTREVJYQTMKYRDMFD"
    plaintext = "BETWEENSUBTLESHADINGANDTHEABSENCEOFLIGHTLIESTHENUANCEOFIQLUSION"
    assert tuple(ciphertext) == pasc.pasc_encrypt(
        plaintext, key, pasc.quagmire3_tr(alphabet)
    )
    assert tuple(plaintext) == pasc.pasc_decrypt(
        ciphertext, key, pasc.quagmire3_tr(alphabet)
    )


def test_quagmire3_kryptos2() -> None:
    """K2 - this is the corrected version with the extra `S`."""
    alphabet = masc.keywordkey("ABCDEFGHIJKLMNOPQRSTUVWXYZ", "KRYPTOS")
    key = "ABSCISSA"
    ciphertext = "VFPJUDEEHZWETZYVGWHKKQETGFQJNCEGGWHKKDQMCPFQZDQMMIAGPFXHQRLGTIMVMZJANQLVKQEDAGDVFRPJUNGEUNAQZGZLECGYUXUEENJTBJLBQCRTBJDFHRRYIZETKZEMVDUFKSJHKFWHKUWQLSZFTIHHDDDUVHDWKBFUFPWNTDFIYCUQZEREEVLDKFEZMOQQJLTTUGSYQPFEUNLAVIDXFLGGTEZFKZBSFDQVGOGIPUFXHHDRKFFHQNTGPUAECNUVPDJMQCLQUMUNEDFQELZZVRRGKFFVOEEXBDMVPNFQXEZLGREDNQFMPNZGLFLPMRJQYALMGNUVPDXVKPDQUMEBEDMHDAFMJGZNUPLGESWJLLAETG"
    plaintext = "ITWASTOTALLYINVISIBLEHOWSTHATPOSSIBLETHEYUSEDTHEEARTHSMAGNETICFIELDXTHEINFORMATIONWASGATHEREDANDTRANSMITTEDUNDERGRUUNDTOANUNKNOWNLOCATIONXDOESLANGLEYKNOWABOUTTHISTHEYSHOULDITSBURIEDOUTTHERESOMEWHEREXWHOKNOWSTHEEXACTLOCATIONONLYWWTHISWASHISLASTMESSAGEXTHIRTYEIGHTDEGREESFIFTYSEVENMINUTESSIXPOINTFIVESECONDSNORTHSEVENTYSEVENDEGREESEIGHTMINUTESFORTYFOURSECONDSWESTXLAYERTWO"
    assert tuple(ciphertext) == pasc.pasc_encrypt(
        plaintext, key, pasc.quagmire3_tr(alphabet)
    )
    assert tuple(plaintext) == pasc.pasc_decrypt(
        ciphertext, key, pasc.quagmire3_tr(alphabet)
    )


def test_quagmire4() -> None:
    """ """
    return
    # alphabet = masc.keywordkey("ABCDEFGHIJKLMNOPQRSTUVWXYZ", "PAULBRANDT")
    # tr = pasc.quagmire4_tr(alphabet)
    # key = "BRANDT"
    # plaintext = "DONTLETANYONETELLYOUTHESKYISTHELIMITWHENTHEREAREFOOTPRINTSONTHEMOON"
    # ciphertext = "KFBIFICEWQVIICOSXRXNCSBLSNMQLNDCSQJLJEKIGIOVDDHIGYFANHMDLHJGKLFXFJG"
    # assert tuple(ciphertext) == pasc.pasc_encrypt(plaintext, key, tr)
    # assert tuple(plaintext) == pasc.pasc_decrypt(ciphertext, key, tr)


"""
From: https://sites.google.com/site/cryptocrackprogram/user-guide/cipher-types/substitution/quagmire

Type: Quagmire 1
Plaintext keyword: PAULBRANDT
Indicator keyword: BRANDT
Indicator position: A
Encipher the following Paul Brandt quote "Don’t let anyone tell you the sky is the limit when there are footprints on the moon.” gives:

    Plaintext:  dontle tanyon etelly outhes kyisth elimit whenth ereare footpr intson themoo n
    Ciphertext: HIFUFC IRFKUY KYJPFQ SSHZMM QONGKF KTNDQA WDJSKF KVJNHC LIRUCX OWHGUY IDJDUK G
"""

"""
Type: Quagmire 2

Ciphertext keyword: PAULBRANDT
Indicator keyword: BRANDT
Indicator position: C
Encipher the following Paul Brandt quote "Don’t let anyone tell you the sky is the limit when there are footprints on the moon.” gives:

    Plaintext:  dontle tanyon etelly outhes kyisth elimit whenth ereare footpr intson themoo n
    Ciphertext: RMGXKE VLGUQQ NWLJKB KXOFCY GADWYH NIDKHZ YELMYH NSLBWE DMHXSX EKOWQQ VELKQS J

Type: Quagmire 3
Plain/Ciphertext keywords: PAULBRANDT
Indicator keyword: BRANDT
Indicator position: P
Encipher the following Paul Brandt quote "Don’t let anyone tell you the sky is the limit when there are footprints on the moon.” gives:

    Plaintext:  dontle tanyon etelly outhes kyisth elimit whenth ereare footpr intson themoo n
    Ciphertext: FXDIEO GNDBZI IHFCEN WDCQMU SLJPJV ITJXVK POFGJV IEFDGO JXQIDH OFCPZI GOFXZP E

Type: Quagmire 4
Plaintext keyword: PAULBRANDT
Ciphertext keyword: BRANDT
Indicator keyword: COUNTRY
Indicator position: P
Encipher the following Paul Brandt quote "Don’t let anyone tell you the sky is the limit when there are footprints on the moon.” gives:

    Plaintext:  dontlet anyonet ellyout heskyis thelimi twhenth erearef ootprin tsonthe moon
    Ciphertext: KFBIFIC EWQVIIC OSXRXNC SBLSNMQ LNDCSQJ LJEKIGI OVDDHIG YFANHMD LHJGKLF XFJG
"""

from aldegonde import masc, pasc

ABC = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def test_vigenere() -> None:
    key = "LEMON"
    plaintext = "ATTACKATDAWN"
    ciphertext = "LXFOPVEFRNHR"
    assert tuple(ciphertext) == tuple(
        e for e in pasc.pasc_encrypt(plaintext, key, pasc.vigenere_tr(ABC))
    )
    assert tuple(plaintext) == tuple(
        e for e in pasc.pasc_decrypt(ciphertext, key, pasc.vigenere_tr(ABC))
    )


def test_vigenere_lanaki() -> None:
    """
    from Lanaki 13. This is the first part of the interruptor test without the interruptor
    """
    key = "BUSINESSMACHINES"
    plaintext = "AMMUNITIONFORFIRSTARTILL"
    ciphertext = "BOLYRPJDROJKXTPFYXSXBPUU"
    TR = pasc.quagmire2_tr(ABC, "HYDRAULIC", key, "A")
    assert tuple(ciphertext) == tuple(e for e in pasc.pasc_encrypt(plaintext, key, TR))
    assert tuple(plaintext) == tuple(e for e in pasc.pasc_decrypt(ciphertext, key, TR))


def test_vigenere_ciphertext_interrupted() -> None:
    """
    From Lanaki chapter 13
    """
    key = "BUSINESSMACHINES"
    plaintext = (
        "AMMUNITIONFORFIRSTARTILLERYWILLBELOADEDAFTERAMMUNITIONFORTHIRDARTILLERY"
    )
    ciphertext = (
        "BOLYRPJDROJKXTPFYXSXBPUUQHRNMYTTXHPCRFQBEJFIELLBONQOQVECXBODFPAZQONUFIC"
    )
    TR = pasc.quagmire2_tr(ABC, "HYDRAULIC", key, "A")
    interruptor = "Q"
    assert tuple(ciphertext) == tuple(
        e
        for e in pasc.pasc_encrypt_interrupted(
            plaintext, key, TR, ciphertext_interruptor=interruptor
        )
    )
    assert tuple(plaintext) == tuple(
        e
        for e in pasc.pasc_decrypt_interrupted(
            ciphertext, key, TR, ciphertext_interruptor=interruptor
        )
    )


def test_vigenere_plaintext_interrupted() -> None:
    """
    From Lanaki chapter 13
    """
    key = "BUSINESSMACHINES"
    plaintext = (
        "AMMUNITIONFORFIRSTARTILLERYWILLBELOADEDAFTERAMMUNITIONFORTHIRDARTILLERY"
    )
    ciphertext = (
        "BOLYRPJDROJKXKJFYXSXDJUPSYIYDPYFXURAFAENMJJVBOLYRPJDROJKXDGDXGUFDJUPSYI"
    )
    TR = pasc.quagmire2_tr(ABC, "HYDRAULIC", key, "A")
    interruptor = "R"
    assert tuple(ciphertext) == tuple(
        e
        for e in pasc.pasc_encrypt_interrupted(
            plaintext, key, TR, plaintext_interruptor=interruptor
        )
    )
    assert tuple(plaintext) == tuple(
        e
        for e in pasc.pasc_decrypt_interrupted(
            ciphertext, key, TR, plaintext_interruptor=interruptor
        )
    )


def test_beaufort() -> None:
    key = "FORTIFICATION"
    plaintext = "DEFENDTHEEASTWALLOFTHECASTLE"
    ciphertext = "CKMPVCPVWPIWUJOGIUAPVWRIWUUK"
    assert tuple(ciphertext) == tuple(
        e for e in pasc.pasc_encrypt(plaintext, key, pasc.beaufort_tr(ABC))
    )
    assert tuple(plaintext) == tuple(
        e for e in pasc.pasc_decrypt(ciphertext, key, pasc.beaufort_tr(ABC))
    )


def test_variantbeaufort() -> None:
    key = "CIPHER"
    plaintext = "HONESTYISTHEBESTPOLICY"
    ciphertext = "FGYXOCWADMDNZWDMLXJANR"
    assert tuple(ciphertext) == tuple(
        e for e in pasc.pasc_encrypt(plaintext, key, pasc.variantbeaufort_tr(ABC))
    )
    assert tuple(plaintext) == tuple(
        e for e in pasc.pasc_decrypt(ciphertext, key, pasc.variantbeaufort_tr(ABC))
    )


def test_quagmire1() -> None:
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    keyword = "PAULBRANDT"
    key = "BRANDT"
    TR = pasc.quagmire1_tr(alphabet, keyword, key)
    plaintext = "DONTLETANYONETELLYOUTHESKYISTHELIMITWHENTHEREAREFOOTPRINTSONTHEMOON"
    ciphertext = "HIFUFCIRFKUYKYJPFQSSHZMMQONGKFKTNDQAWDJSKFKVJNHCLIRUCXOWHGUYIDJDUKG"
    assert tuple(ciphertext) == tuple(pasc.pasc_encrypt(plaintext, key, TR))
    assert tuple(plaintext) == tuple(pasc.pasc_decrypt(ciphertext, key, TR))


def test_quagmire1_aca() -> None:
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    keyword = "SPRINGFEVER"
    key = "FLOWER"
    TR = pasc.quagmire1_tr(alphabet, keyword, key)
    plaintext = "THEQUAGONEISAPERIODICCIPHERWITHAKEYEDPLAINALPHABETRUNAGAINSTASTRAIGHTCIPHERALPHABET"
    ciphertext = "QPMGQRBUJUYIFDMPYAIFQYYJJJHJYCJLUUTPIDVWYMFSGAESDWHIZRBLIRVCFCZPELBPZYYJJJHWLJJLPUP"
    assert tuple(ciphertext) == tuple(pasc.pasc_encrypt(plaintext, key, TR))
    assert tuple(plaintext) == tuple(pasc.pasc_decrypt(ciphertext, key, TR))


def test_quagmire2() -> None:
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    keyword = "PAULBRANDT"
    key = "BRANDT"
    TR = pasc.quagmire2_tr(alphabet, keyword, key, indicator="C")
    plaintext = "DONTLETANYONETELLYOUTHESKYISTHELIMITWHENTHEREAREFOOTPRINTSONTHEMOON"
    ciphertext = "RMGXKEVLGUQQNWLJKBKXOFCYGADWYHNIDKHZYELMYHNSLBWEDMHXSXEKOWQQVELKQSJ"
    assert tuple(ciphertext) == tuple(pasc.pasc_encrypt(plaintext, key, TR))
    assert tuple(plaintext) == tuple(pasc.pasc_decrypt(ciphertext, key, TR))


def test_quagmire3() -> None:
    """ """
    alphabet = masc.mixedalphabet("ABCDEFGHIJKLMNOPQRSTUVWXYZ", "PAULBRANDT")
    key = "BRANDT"
    plaintext = "DONTLETANYONETELLYOUTHESKYISTHELIMITWHENTHEREAREFOOTPRINTSONTHEMOON"
    ciphertext = "FXDIEOGNDBZIIHFCENWDCQMUSLJPJVITJXVKPOFGJVIEFDGOJXQIDHOFCPZIGOFXZPE"
    assert tuple(ciphertext) == tuple(
        e for e in pasc.pasc_encrypt(plaintext, key, pasc.quagmire3_tr(alphabet))
    )
    assert tuple(plaintext) == tuple(
        e for e in pasc.pasc_decrypt(ciphertext, key, pasc.quagmire3_tr(alphabet))
    )


def test_quagmire3_kryptos1() -> None:
    """K1."""
    alphabet = masc.mixedalphabet("ABCDEFGHIJKLMNOPQRSTUVWXYZ", "KRYPTOS")
    key = "PALIMPSEST"
    ciphertext = "EMUFPHZLRFAXYUSDJKZLDKRNSHGNFIVJYQTQUXQBQVYUVLLTREVJYQTMKYRDMFD"
    plaintext = "BETWEENSUBTLESHADINGANDTHEABSENCEOFLIGHTLIESTHENUANCEOFIQLUSION"
    assert tuple(ciphertext) == tuple(
        e for e in pasc.pasc_encrypt(plaintext, key, pasc.quagmire3_tr(alphabet))
    )
    assert tuple(plaintext) == tuple(
        e for e in pasc.pasc_decrypt(ciphertext, key, pasc.quagmire3_tr(alphabet))
    )


def test_quagmire3_kryptos2() -> None:
    """K2 - this is the corrected version with the extra `S`."""
    alphabet = masc.mixedalphabet("ABCDEFGHIJKLMNOPQRSTUVWXYZ", "KRYPTOS")
    key = "ABSCISSA"
    ciphertext = "VFPJUDEEHZWETZYVGWHKKQETGFQJNCEGGWHKKDQMCPFQZDQMMIAGPFXHQRLGTIMVMZJANQLVKQEDAGDVFRPJUNGEUNAQZGZLECGYUXUEENJTBJLBQCRTBJDFHRRYIZETKZEMVDUFKSJHKFWHKUWQLSZFTIHHDDDUVHDWKBFUFPWNTDFIYCUQZEREEVLDKFEZMOQQJLTTUGSYQPFEUNLAVIDXFLGGTEZFKZBSFDQVGOGIPUFXHHDRKFFHQNTGPUAECNUVPDJMQCLQUMUNEDFQELZZVRRGKFFVOEEXBDMVPNFQXEZLGREDNQFMPNZGLFLPMRJQYALMGNUVPDXVKPDQUMEBEDMHDAFMJGZNUPLGESWJLLAETG"
    plaintext = "ITWASTOTALLYINVISIBLEHOWSTHATPOSSIBLETHEYUSEDTHEEARTHSMAGNETICFIELDXTHEINFORMATIONWASGATHEREDANDTRANSMITTEDUNDERGRUUNDTOANUNKNOWNLOCATIONXDOESLANGLEYKNOWABOUTTHISTHEYSHOULDITSBURIEDOUTTHERESOMEWHEREXWHOKNOWSTHEEXACTLOCATIONONLYWWTHISWASHISLASTMESSAGEXTHIRTYEIGHTDEGREESFIFTYSEVENMINUTESSIXPOINTFIVESECONDSNORTHSEVENTYSEVENDEGREESEIGHTMINUTESFORTYFOURSECONDSWESTXLAYERTWO"
    assert tuple(ciphertext) == tuple(
        e for e in pasc.pasc_encrypt(plaintext, key, pasc.quagmire3_tr(alphabet))
    )
    assert tuple(plaintext) == tuple(
        e for e in pasc.pasc_decrypt(ciphertext, key, pasc.quagmire3_tr(alphabet))
    )


def test_quagmire4() -> None:
    """ """
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    ptkeyword = "PAULBRANDT"
    ctkeyword = "BRANDT"
    key = "COUNTRY"
    indicator = "P"
    TR = pasc.quagmire4_tr(alphabet, ptkeyword, ctkeyword, key, indicator)
    plaintext = "DONTLETANYONETELLYOUTHESKYISTHELIMITWHENTHEREAREFOOTPRINTSONTHEMOON"
    ciphertext = "KFBIFICEWQVIICOSXRXNCSBLSNMQLNDCSQJLJEKIGIOVDDHIGYFANHMDLHJGKLFXFJG"
    assert tuple(ciphertext) == tuple(pasc.pasc_encrypt(plaintext, key, TR))
    assert tuple(plaintext) == tuple(pasc.pasc_decrypt(ciphertext, key, TR))


def test_quagmire4_aca() -> None:
    """ """
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    ptkeyword = "SENSORY"
    ctkeyword = "PERCEPTION"
    key = "EXTRA"
    indicator = "S"
    TR = pasc.quagmire4_tr(alphabet, ptkeyword, ctkeyword, key, indicator)
    plaintext = "THISONEEMPLOYSTHREEKEYWORDS"
    ciphertext = "VBMRFCYISPMPBRRHEICXRREIGDX"
    assert tuple(ciphertext) == tuple(pasc.pasc_encrypt(plaintext, key, TR))
    assert tuple(plaintext) == tuple(pasc.pasc_decrypt(ciphertext, key, TR))


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

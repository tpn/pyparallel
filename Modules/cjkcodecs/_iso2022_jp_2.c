/*
 * _iso2022_jp_2.c: the ISO-2022-JP-2 codec (RFC1554)
 *
 * Written by Hye-Shik Chang <perky@FreeBSD.org>
 * $CJKCodecs: _iso2022_jp_2.c,v 1.8 2003/12/31 05:46:55 perky Exp $
 */

#define ISO2022_DESIGNATIONS \
        CHARSET_ASCII, CHARSET_JISX0201_R, CHARSET_JISX0208, \
        CHARSET_JISX0208_O, CHARSET_JISX0212, CHARSET_GB2312, \
        CHARSET_KSX1001, CHARSET_JISX0212, \
        CHARSET_ISO8859_1, CHARSET_ISO8859_7
#define ISO2022_USE_G2_DESIGNATION  yo!
#define ISO2022_USE_JISX0208EXT

#include "codeccommon.h"
#include "iso2022common.h"
#include "alg_jisx0201.h"
#include "alg_iso8859_1.h"
#include "alg_iso8859_7.h"

ENCMAP(jisxcommon)
DECMAP(jisx0208)
DECMAP(jisx0212)
ENCMAP(cp949)
DECMAP(ksx1001)
ENCMAP(gbcommon)
DECMAP(gb2312)

#define HAVE_ENCODER_INIT
ENCODER_INIT(iso2022_jp_2)
{
    STATE_CLEARFLAGS(state)
    STATE_SETG0(state, CHARSET_ASCII)
    STATE_SETG1(state, CHARSET_ASCII)
    STATE_SETG2(state, CHARSET_ASCII)
    return 0;
}

#define HAVE_ENCODER_RESET
ENCODER_RESET(iso2022_jp_2)
{
    if (STATE_GETG0(state) != CHARSET_ASCII) {
        WRITE3(ESC, '(', 'B')
        STATE_SETG0(state, CHARSET_ASCII)
        NEXT_OUT(3)
    }
    return 0;
}

ENCODER(iso2022_jp_2)
{
    while (inleft > 0) {
        Py_UNICODE  c = IN1;
        DBCHAR      code;

        if (c < 0x80) {
            switch (STATE_GETG0(state)) {
            case CHARSET_ASCII:
                WRITE1(c)
                NEXT(1, 1)
                break;
            case CHARSET_JISX0201_R:
                JISX0201_R_ENCODE(c, code)
                else { /* FALLTHROUGH (yay!) */
            default:
                    WRITE3(ESC, '(', 'B')
                    NEXT_OUT(3)
                    STATE_SETG0(state, CHARSET_ASCII)
                    code = c;
                }
                WRITE1(code)
                NEXT(1, 1)
                break;
            }
            if (c == '\n')
                STATE_CLEARFLAG(state, F_SHIFTED)
        }
        else UCS4INVALID(c)
        else {
            unsigned char    charset;

            charset = STATE_GETG0(state);
            if (charset == CHARSET_JISX0201_R) {
                code = DBCINV;
                JISX0201_R_ENCODE(c, code)
                if (code != DBCINV) {
                    WRITE1(code)
                    NEXT(1, 1)
                    continue;
                }
            }

            TRYMAP_ENC(jisxcommon, code, c) {
                if (code & 0x8000) { /* MSB set: JIS X 0212 */
                    if (charset != CHARSET_JISX0212) {
                        WRITE4(ESC, '$', '(', 'D')
                        STATE_SETG0(state, CHARSET_JISX0212)
                        NEXT_OUT(4)
                    }
                    WRITE2((code >> 8) & 0x7f, code & 0x7f)
                } else { /* MSB unset: JIS X 0208 */
jisx0208encode:     if (charset != CHARSET_JISX0208) {
                        WRITE3(ESC, '$', 'B')
                        STATE_SETG0(state, CHARSET_JISX0208)
                        NEXT_OUT(3)
                    }
                    WRITE2(code >> 8, code & 0xff)
                }
                NEXT(1, 2)
            } else TRYMAP_ENC(cp949, code, c) {
                if (code & 0x8000) /* MSB set: CP949 */
                    return 2;
                if (charset != CHARSET_KSX1001) {
                    WRITE4(ESC, '$', '(', 'C')
                    STATE_SETG0(state, CHARSET_KSX1001)
                    NEXT_OUT(4)
                }
                WRITE2(code >> 8, code & 0xff)
                NEXT(1, 2)
            } else TRYMAP_ENC(gbcommon, code, c) {
                if (code & 0x8000) /* MSB set: GBK */
                    return 2;
                if (charset != CHARSET_GB2312) {
                    WRITE4(ESC, '$', '(', 'A')
                    STATE_SETG0(state, CHARSET_GB2312)
                    NEXT_OUT(4)
                }
                WRITE2(code >> 8, code & 0xff)
                NEXT(1, 2)
            } else if (c == 0xff3c) { /* FULL-WIDTH REVERSE SOLIDUS */
                code = 0x2140;
                goto jisx0208encode;
            } else {
                JISX0201_R_ENCODE(c, code)
                else {
                    /* There's no need to try to encode as ISO-8859-1 or
                     * ISO-8859-7 because JIS X 0212 includes them already.
                     */
                    return 1;
                }
                /* if (charset == CHARSET_JISX0201_R) : already checked */
                WRITE4(ESC, '(', 'J', code)
                STATE_SETG0(state, CHARSET_JISX0201_R)
                NEXT(1, 4)
            }
        }
    }

    return 0;
}

#define HAVE_DECODER_INIT
DECODER_INIT(iso2022_jp_2)
{
    STATE_CLEARFLAGS(state)
    STATE_SETG0(state, CHARSET_ASCII)
    STATE_SETG1(state, CHARSET_ASCII)
    STATE_SETG2(state, CHARSET_ASCII)
    return 0;
}

#define HAVE_DECODER_RESET
DECODER_RESET(iso2022_jp_2)
{
    STATE_CLEARFLAG(state, F_SHIFTED)
    return 0;
}

DECODER(iso2022_jp_2)
{
  ISO2022_LOOP_BEGIN
    unsigned char    charset, c2;

    ISO2022_GETCHARSET(charset, c)

    if (charset & CHARSET_DOUBLEBYTE) {
        RESERVE_INBUF(2)
        RESERVE_OUTBUF(1)
        c2 = IN2;
        if (charset == CHARSET_JISX0208 || charset == CHARSET_JISX0208_O) {
            if (c == 0x21 && c2 == 0x40) /* FULL-WIDTH REVERSE SOLIDUS */
                **outbuf = 0xff3c;
            else TRYMAP_DEC(jisx0208, **outbuf, c, c2);
            else return 2;
        } else if (charset == CHARSET_JISX0212) {
            TRYMAP_DEC(jisx0212, **outbuf, c, c2);
            else return 2;
        } else if (charset == CHARSET_KSX1001) {
            TRYMAP_DEC(ksx1001, **outbuf, c, c2);
            else return 2;
        } else if (charset == CHARSET_GB2312) {
            TRYMAP_DEC(gb2312, **outbuf, c, c2);
            else return 2;
        } else
            return MBERR_INTERNAL;
        NEXT(2, 1)
    } else if (charset == CHARSET_ASCII) {
        RESERVE_OUTBUF(1)
        OUT1(c)
        NEXT(1, 1)
    } else if (charset == CHARSET_JISX0201_R) {
        RESERVE_OUTBUF(1)
        JISX0201_R_DECODE(c, **outbuf)
        else
            return 1;
        NEXT(1, 1)
    } else
        return MBERR_INTERNAL;
  ISO2022_LOOP_END

  return 0;
}

#include "codecentry.h"
BEGIN_CODEC_REGISTRY(iso2022_jp_2)
    MAPOPEN(ja_JP)
        IMPORTMAP_DEC(jisx0208)
        IMPORTMAP_DEC(jisx0212)
        IMPORTMAP_ENC(jisxcommon)
    MAPCLOSE()
    MAPOPEN(ko_KR)
        IMPORTMAP_ENC(cp949)
        IMPORTMAP_DEC(ksx1001)
    MAPCLOSE()
    MAPOPEN(zh_CN)
        IMPORTMAP_ENC(gbcommon)
        IMPORTMAP_DEC(gb2312)
    MAPCLOSE()
END_CODEC_REGISTRY(iso2022_jp_2)

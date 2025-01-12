'''
在线验证邮箱真实性
'''

import random
import smtplib
import logging
import time

import dns.resolver

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(filename)s [line:%(lineno)d] - %(levelname)s: %(message)s')

logger = logging.getLogger()


def fetch_mx(host):
    '''
    解析服务邮箱
    :param host:
    :return:
    '''
    logger.info('正在查找邮箱服务器')
    answers = dns.resolver.query(host, 'MX')
    res = [str(rdata.exchange)[:-1] for rdata in answers]
    logger.info('查找结果为：%s' % res)
    return res

results=[]
def verify_istrue(email):
    '''
    :param email:
    :return:
    '''
    email_list = []
    email_obj = {}
    final_res = {}

    if isinstance(email, str) or isinstance(email, bytes):
        email_list.append(email)
    else:
        email_list = email

    for em in email_list:
        name, host = em.split('@')
        if email_obj.get(host):
            email_obj[host].append(em)
        else:
            email_obj[host] = [em]

    for key in email_obj.keys():
        host = random.choice(fetch_mx(key))
        logger.info('正在连接服务器...：%s' % host)
        logger.info("已经屏蔽了所有的错误logger，现在是单线程。")
        s = smtplib.SMTP(host, timeout=10)
        for need_verify in email_obj[key]:
            helo = s.docmd('HELO chacuo.net')
            #logger.debug(helo)
            try:
                send_from = s.docmd('MAIL FROM:<asd@qq.com>')
            except:
                s = smtplib.SMTP(host, timeout=10)
                send_from = s.docmd('MAIL FROM:<asd@qq.com>')
            #logger.debug(send_from)
            send_from = s.docmd('RCPT TO:<%s>' % need_verify)
            #logger.debug(send_from)
            if send_from[0] == 250 or send_from[0] == 451:
                final_res[need_verify] = True  # 存在
                logger.info('%s 存在' % need_verify)
                results.append(need_verify)
            elif send_from[0] == 550:
                final_res[need_verify] = False  # 不存在
            else:
                final_res[need_verify] = None  # 未知

        s.close()

    return final_res


if __name__ == '__main__':
    with open ('email.txt','r') as f:
        emails=f.readlines()
        emails = [email.strip()+"@xxx.com" for email in emails]
    #print(emails)
    verify_istrue(emails)
    print(results)

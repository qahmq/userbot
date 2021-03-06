import html

from userbot import jmthon

from ..core.managers import edit_or_reply
from ..sql_helper import warns_sql as sql

plugin_category = "admin"


@jmthon.ar_cmd(
    pattern="تحذير(?:\s|$)([\s\S]*)",
    command=("تحذير", plugin_category),
    info={
        "header": "لتحذير المستخدم.",
        "description": "بالرد على المستخدم لتحذيره .",
        "usage": "{tr}تحذير <السبب>",
    },
)
async def _(event):
    "لتحذير المستخدم"
    warn_reason = event.pattern_match.group(1)
    if not warn_reason:
        warn_reason = "- لا يوجد سبب ، 🗒"
    reply_message = await event.get_reply_message()
    limit, soft_warn = sql.get_warn_setting(event.chat_id)
    num_warns, reasons = sql.warn_user(
        reply_message.sender_id, event.chat_id, warn_reason
    )
    if num_warns >= limit:
        sql.reset_warns(reply_message.sender_id, event.chat_id)
        if soft_warn:
            logger.info("TODO: طرد المستخدم")
            reply = "**▸┊بسبب تخطي التحذيرات الـ {} ، يجب طرد المستخدم! 🚷**".format(
                limit, reply_message.sender_id
            )
        else:
            logger.info("TODO: حظر المستخدم")
            reply = "**▸┊بسبب تخطي التحذيرات الـ {} ، يجب حظر المستخدم! ⛔️**".format(
                limit, reply_message.sender_id
            )
    else:
        reply = "**▸┊[ المستخدم 👤](tg://user?id={}) **لديه {}/{} تحذيرات ، احذر!****".format(
            reply_message.sender_id, num_warns, limit
        )
        if warn_reason:
            reply += "\n**▸┊سبب التحذير الأخير **\n{}".format(html.escape(warn_reason))
    await edit_or_reply(event, reply)

@jmthon.ar_cmd(
    pattern="التحذيرات",
    command=("التحذيرات", plugin_category),
    info={
        "header": "لعرض تحذيرات المستخدمين.",
        "usage": "{tr}التحذيرات <بالرد>",
    },
)
async def _(event):
    "لعرض تحذيرات المستخدمين"
    reply_message = await event.get_reply_message()
    if not reply_message:
        return await edit_delete(event, "**▸┊قم بالرد ع المستخدم للحصول ع تحذيراته . ☻**")
    result = sql.get_warns(reply_message.sender_id, event.chat_id)
    if not result or result[0] == 0:
        return await edit_or_reply(event, "__▸┊هذا المستخدم ليس لديه أي تحذير! ツ__")
    num_warns, reasons = result
    limit, soft_warn = sql.get_warn_setting(event.chat_id)
    if not reasons:
        return await edit_or_reply(
            event,
            "**▸┊[ المستخدم 👤](tg://user?id={}) **لديه {}/{} تحذيرات ، لكن لا توجد اسباب !**".format(
                num_warns, limit
            ),
        )

    text = "**▸┊[ المستخدم 👤](tg://user?id={}) **لديه {}/{} تحذيرات ، للأسباب : ↶**".format(
        num_warns, limit
            )

    text = "**▸┊ المستخدم لديه {}/{} تحذيرات ، للأسباب : ↶:".format(
        num_warns, limit
    )
    text += "\r\n"
    text += reasons
    await event.edit(text)

@jmthon.ar_cmd(
    pattern="حذف التحذير(?: |$)(.*)",
    command=("التحذيرات", plugin_category))
async def _(event):
    reply_message = await event.get_reply_message()
    sql.reset_warns(reply_message.sender_id, event.chat_id)
    await edit_or_reply(event, "**▸┊تم إعادة ضبط التحذيرات!**")

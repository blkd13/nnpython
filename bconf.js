'use strict';
BOAT.betconf_controller = function () {
    var SCREEN_ID_TOUJITSU = "D628";
    var SCREEN_ID_ZENJITSU = "D728";
    var OPERATION_KBN_TOJITSU = "2";
    var OPERATION_KBN_ZENJITSU = "3";
    var _isSubmitted = false;
    var clientErrorMapping = { "06029": "amount", "06030": "pass", "06031": "amount", "06080": "amount" };
    function init() {
        var betStatusList = BOAT.betconf_service.getBetStatusList();
        $(".setOdds").each(function (idx, self) {
            var setOddsId = $(self).attr("id");
            var keys = setOddsId.split("_");
            var kachishiki = keys[3];
            var odds = BOAT.betconf_service.getOdds(keys[1],
                keys[2], kachishiki, keys[4]);
            var betStatus = betStatusList[idx];
            var oddsValue = _setupOddsValue(betStatus.isAbsence, betStatus.isAvailable, kachishiki, odds.oddsValue);
            var minOddsValue = _setupMinMaxOddsValue(betStatus.isAbsence, betStatus.isAvailable, kachishiki, odds.minOddsValue);
            var maxOddsValue = _setupMinMaxOddsValue(betStatus.isAbsence, betStatus.isAvailable, kachishiki, odds.maxOddsValue);
            $(self).html(_setupOdds(oddsValue, minOddsValue, maxOddsValue))
        });
        BOAT.screen.createScrollBar(200, "voteListAreaInner");
        BOAT.screenId.setScreenIdInit(_getScreenId());
        BOAT.event_handler.on($("#confirmationArea"), {
            "event": "click", "selector": "#amountKey", "func": function () {
                BOAT.key_controller.open({ "isNumericKey": true, "isAmount": true, "zeroCount": 0, "invokerItemId": "amount", "maxLength": 8 })
            }
        });
        BOAT.event_handler.on($("#confirmationArea"), {
            "event": "click", "selector": "#passKey", "func": function () {
                BOAT.key_controller.open({ "invokerItemId": "pass", "maxLength": 10 })
            }
        });
        BOAT.event_handler.on($("#confirmationArea"), {
            "event": "click", "selector": "#modifyBet", "func": function () {
                if (_isSubmitted) return;
                _isSubmitted = true;
                var urlParam = BOAT.betconf_service.getBetcomURLParam();
                _makeForm(urlParam);
                $("#betconfForm input[name=operationKbn]").val(_getOperationKbn());
                $("#betconfForm").trigger("submit")
            }
        });
        BOAT.event_handler.on($("#confirmationArea"), {
            "event": "click", "selector": "#submitBet", "func": function () {
                $("#amount").removeClass("clientError");
                $("#pass").removeClass("clientError");
                var cheError = BOAT.betconf_service.validate($("#amount").val(), $("#pass").val());
                if (cheError.isErrorDisp) {
                    var errorCode = cheError.errorCode;
                    $("#" + clientErrorMapping[errorCode]).addClass("clientError");
                    BOAT.popup_controller.open({
                        "messageCode": errorCode,
                        "messageReplace": cheError.errorMessages,
                        datetime: moment().format("YYYYMMDDHHmmss"),
                        "screenType": BOAT.popup_controller.SCREEN_TYPE.POPUP_OK
                    })
                } else {
                    if (_isSubmitted) return;
                    BOAT.popup_controller.open({
                        "messageCode": "06111",
                        "screenType": BOAT.popup_controller.SCREEN_TYPE.ATTENTION_OK_CANCEL,
                        "callbackOk": function () {
                            if (_isSubmitted) return;
                            _isSubmitted = true;
                            var urlParam = BOAT.betconf_service.getBetcompURLParam();
                            _makeForm(urlParam);
                            $("#betconfForm").trigger("submit")
                        }
                    })
                }
            }
        })
    } function _getScreenId() {
        if (BOAT.attribute.isZenjitsuHatsubaiJyo) return SCREEN_ID_ZENJITSU;
        else return SCREEN_ID_TOUJITSU
    } function _getOperationKbn() {
        if (BOAT.attribute.isZenjitsuHatsubaiJyo) return OPERATION_KBN_ZENJITSU;
        else return OPERATION_KBN_TOJITSU
    } function _setupOdds(oddsValue, minOddsValue, maxOddsValue) {
        if (oddsValue === "") if (minOddsValue === "---.-" && maxOddsValue === "---.-") return minOddsValue;
        else return minOddsValue + "-" + maxOddsValue;
        else return oddsValue
    } function _setupOddsValue(isAbsence, isAvailable, kachishiki, oddsValue) {
        if (_isFukuKaku(kachishiki)) return "";
        if (isAbsence || !isAvailable) return "---.-";
        if (oddsValue) return _setupRed(oddsValue);
        else return "---.-"
    } function _setupMinMaxOddsValue(isAbsence, isAvailable, kachishiki, oddsValue) {
        if (!_isFukuKaku(kachishiki)) return "";
        if (isAbsence || !isAvailable) return "---.-";
        if (oddsValue) return _setupRed(oddsValue);
        else return "---.-"
    } function _isFukuKaku(kachishiki) {
        if (kachishiki === "2" || kachishiki ===
            "5") return true;
        return false
    } function _setupRed(value) {
        var odds = BOAT.common_utils.parseNumber(value);
        if (odds >= 1E3) odds = Math.floor(odds);
        else {
            odds = Math.floor(odds * 10) / 10;
            if (odds.toString().indexOf(".") < 0) odds = odds + ".0"
        } if (odds >= 1E3 || odds === "0.0") return "<strong>" + odds + "</strong>";
        else return odds.toString()
    } function _makeForm(urlParam) {
        $("#betconfForm").attr("action", urlParam.url);
        var param = urlParam.param;
        var $input = null;
        $.each(param, function (key, value) {
            $input = $("<input>");
            $input.attr("type", "hidden");
            $input.attr("name", key);
            $input.val(value);
            $("#betconfForm").append($input)
        })
    } function viewAttention() {
        var currentBetLimitAmount = BOAT.global.header.currentBetLimitAmount;
        var totalBetAmount = $("#betconfTotalBetAmount").html().replace(/,/g, "");
        var target = $("#shortBalance");
        if (currentBetLimitAmount < totalBetAmount) {
            if (!target.hasClass("attention")) {
                target.addClass("attention");
                target.html("\u6b8b\u9ad8\u91d1\u984d\u304c\u4e0d\u8db3\u3057\u3066\u304a\u308a\u307e\u3059")
            }
        } else target.removeClass("attention").html("")
    }
    return { init: init, viewAttention: viewAttention }
} ();
$(function () {
    BOAT.header_controller.init({ "func": BOAT.betconf_controller.viewAttention });
    BOAT.betconf_controller.init()
});



'use strict';
BOAT.betconf_service = function () {
    var BET_WAY_ODDS = "5";
    var SCREEN_FROM_TOUJITSU = "D628";
    var SCREEN_FROM_ZENJITSU = "D728";
    var UNFOLDEDFLG_CLOSE = "0";
    function getBetcomURLParam() {
        var urlKey;
        var param;
        if (BOAT.attribute.isZenjitsuHatsubaiJyo) if (BOAT.attribute.betWay === BET_WAY_ODDS) {
            urlKey = "url_betcom_006";
            param = _getParamZenjitsu()
        } else {
            urlKey = "url_betcom_005";
            param = _getParamRegZenjitsu()
        } else if (BOAT.attribute.betWay === BET_WAY_ODDS) {
            urlKey = "url_betcom_003";
            param = _getParamToujitsu()
        } else {
            urlKey =
                "url_betcom_002";
            param = _getParamRegToujitsu()
        } var ret = { url: _getUrl(urlKey), param: param };
        return ret
    }
    function _getUrl(urlKey) {
        var _contextPath = $("meta[name='contextPath']").attr("content");
        var url = _contextPath + BOAT.common_utils.getProperty(urlKey);
        url = url + "?";
        url = url + "cid=" + $("meta[name='centerNo']").attr("content");
        url = url + "&";
        url = url + "r=" + BOAT.common_utils.generateRandomID();
        return url
    }
    function _getParamZenjitsu() {
        var param = {
            "screenFrom": _getScreenFrom(), "betWay": BOAT.attribute.betWay, "jyoCode": BOAT.attribute.jyoCode,
            "multiRace": BOAT.attribute.isMultiRace, "selectionRaceNoList": BOAT.attribute.selectionRaceNoList, "lastSelectionKachishiki": BOAT.attribute.lastSelectionKachishiki, "lastSelectionBetWay": BOAT.attribute.lastSelectionBetWay, "lastSelectionRacer": BOAT.attribute.lastSelectionRacer
        };
        return param
    }
    function _getParamRegZenjitsu() {
        var param = {
            "screenFrom": _getScreenFrom(), "betWay": BOAT.attribute.betWay, "jyoCode": BOAT.attribute.jyoCode, "multiRace": BOAT.attribute.isMultiRace, "selectionRaceNoList": BOAT.attribute.selectionRaceNoList,
            "lastSelectionKachishiki": BOAT.attribute.lastSelectionKachishiki
        };
        return param
    }
    function _getParamToujitsu() {
        var param = { "screenFrom": _getScreenFrom(), "betWay": BOAT.attribute.betWay, "multiJyo": BOAT.attribute.isMultiJyo, "selectionJyoList": BOAT.attribute.selectionJyoList, "multiRace": BOAT.attribute.isMultiRace, "selectionRaceNoList": BOAT.attribute.selectionRaceNoList, "lastSelectionKachishiki": BOAT.attribute.lastSelectionKachishiki, "lastSelectionBetWay": BOAT.attribute.lastSelectionBetWay, "lastSelectionRacer": BOAT.attribute.lastSelectionRacer };
        return param
    }
    function _getParamRegToujitsu() {
        var param = { "screenFrom": _getScreenFrom(), "betWay": BOAT.attribute.betWay, "multiJyo": BOAT.attribute.isMultiJyo, "selectionJyoList": BOAT.attribute.selectionJyoList, "multiRace": BOAT.attribute.isMultiRace, "selectionRaceNoList": BOAT.attribute.selectionRaceNoList, "lastSelectionKachishiki": BOAT.attribute.lastSelectionKachishiki };
        return param
    }
    function getBetcompURLParam() {
        var ret = { "url": _getUrl("url_betcomp_001"), "param": _getParamBetcomp() };
        return ret
    }
    function _getParamBetcomp() {
        var param = {
            "screenFrom": _getScreenFrom(),
            "betWay": BOAT.attribute.betWay,
            "jyoCode": BOAT.attribute.jyoCode,
            "multiJyo": BOAT.attribute.isMultiJyo,
            "selectionJyoList": BOAT.attribute.selectionJyoList,
            "multiRace": BOAT.attribute.isMultiRace,
            "selectionRaceNoList": BOAT.attribute.selectionRaceNoList,
            "lastSelectionKachishiki": BOAT.attribute.lastSelectionKachishiki,
            "lastSelectionBetWay": BOAT.attribute.lastSelectionBetWay,
            "lastSelectionRacer": BOAT.attribute.lastSelectionRacer
        };
        return param
    }
    function _getScreenFrom() {
        if (BOAT.attribute.isZenjitsuHatsubaiJyo) return SCREEN_FROM_ZENJITSU;
        else return SCREEN_FROM_TOUJITSU
    }
    function validate(betAmount, betPassword) {
        var cheError = { "isErrorDisp": false, "errorCode": "", "errorMessages": [] };
        if (BOAT.common_utils.isHalfNumericError(betAmount)) {
            cheError.isErrorDisp = true;
            cheError.errorCode = "06080";
            cheError.errorMessages = null;
            return cheError
        } if (betAmount === "") {
            cheError.isErrorDisp = true;
            cheError.errorCode = "06029";
            cheError.errorMessages = ["\u8cfc\u5165\u91d1\u984d"];
            return cheError
        } if (betPassword === "") {
            cheError.isErrorDisp = true;
            cheError.errorCode = "06030";
            cheError.errorMessages = ["\u6295\u7968\u7528\u30d1\u30b9\u30ef\u30fc\u30c9"];
            return cheError
        } var numBetAmount = BOAT.common_utils.parseNumber(betAmount);
        if (numBetAmount !== _getBetAmountTotal()) {
            cheError.isErrorDisp = true;
            cheError.errorCode = "06031";
            cheError.errorMessages = ["\u8cfc\u5165\u91d1\u984d"];
            return cheError
        } return cheError
    }
    function _getBetAmountTotal() {
        var betAmountTotal = 0;
        var betListKeys = BOAT.session.getBetListKey();
        $.each(betListKeys, function (idx, key) {
            var sessionBetList = BOAT.session.getBetList(key);
            $.each(sessionBetList.detailInfo, function (idx, detailInfo) { betAmountTotal += _getBetAmount(sessionBetList, detailInfo) })
        });
        return betAmountTotal
    }
    function getBetStatusList() {
        var result = [];
        var betListKeys = BOAT.session.getBetListKey();
        $.each(betListKeys, function (idx, key) {
            var sessionBetList = BOAT.session.getBetList(key);
            var available = sessionBetList.available;
            $.each(sessionBetList.detailInfo, function (idx, detailInfo) {
                var detail = {};
                detail.isAbsence = detailInfo.absence;
                detail.isAvailable = available;
                result[result.length] =
                    detail
            })
        });
        return result
    }
    function _getBetAmount(sessionBetList, detailInfo) {
        if (sessionBetList.unfolded === UNFOLDEDFLG_CLOSE) return sessionBetList.count * 100;
        else return detailInfo.count * 100
    }
    function getOdds(jyoCode, raceNo, kachishiki, kumiban) {
        var betListOdds = BOAT.session.getBetListOdds(jyoCode, raceNo, kachishiki, kumiban);
        return betListOdds
    } return { getBetcomURLParam: getBetcomURLParam, getBetcompURLParam: getBetcompURLParam, validate: validate, getOdds: getOdds, getBetStatusList: getBetStatusList }
} ();



'use strict';
BOAT.common_utils = function () {
    function generateRandomID(min, max) {
        var MIN_VALUE = 1;
        var MAX_VALUE = 1E12;
        var ret = 0;
        var minVal = 0;
        var maxVal = 0;
        if (min === undefined) minVal = MIN_VALUE;
        else minVal = min;
        if (max === undefined) maxVal = MAX_VALUE;
        else maxVal = max;
        if (max > MAX_VALUE) maxVal = MAX_VALUE;
        ret = Math.floor(Math.random() * (maxVal - minVal + 1)) + minVal;
        return Math.abs(ret + +new Date)
    }
    function _getCode(key) {
        if (BOAT.code) {
            var name = BOAT.code[key];
            if (name !== undefined) return name; else return ""
        } else return ""
    }
    function getCodeName(definition, value) {
        return _getCode(definition + "_" + value)
    }
    function getProperty(key) {
        return _getCode(key)
    }
    function parseNumber(value) {
        var number = Number(value);
        if (number === number) return number;
        else return 0
    }
    function parseString(value) { return value + "" } function isHalfNumericError(numberValue) {
        if (numberValue === undefined || numberValue === null || numberValue === "") return false;
        if (String(numberValue).match(/[^0-9]/)) return true;
        else return false
    }
    function isHalfAlphanumericError(alphanumberValue) {
        if (alphanumberValue === undefined ||
            alphanumberValue === null || alphanumberValue === "") return false;
        if (String(alphanumberValue).match(/[^a-zA-Z0-9]/)) return true;
        else return false
    }
    return {
        generateRandomID: generateRandomID,
        getCodeName: getCodeName,
        getProperty: getProperty,
        parseNumber: parseNumber,
        parseString: parseString,
        isHalfNumericError: isHalfNumericError,
        isHalfAlphanumericError: isHalfAlphanumericError
    }
} ();


'use strict';
BOAT.charge_service = function () {
    function open(controller) {
        BOAT.ajax.ajaxCommunication({
            "urlKey": "url_charge_001",
            "data": {},
            "callbackControl": controller,
            "callbackService": _updateGlobalBalance
        })
    }
    function _updateGlobalBalance(data) {
        var headerGlobal = BOAT.global.header;
        headerGlobal.currentBetLimitAmount = data.currentBetLimitAmount;
        headerGlobal.purchasableBetCount = data.purchasableBetCount
    }
    return { open: open }
} ();


'use strict';
BOAT.charge_controller = function () {
    var _useBankCode = "";
    function _displayCharge(data) {
        _useBankCode = data.useBankCode;
        var html = $("#chargeRender").render(data);
        var main = $("#popupMain");
        main.empty();
        $(html).appendTo(main);
        BOAT.screen.loadModalWindow("popupMain");
        BOAT.screenId.setScreenIdMove($("#screenId").html().substr(0, 1) + "634");
        BOAT.header_controller.redrawBalanceInfo(data.updateDate, data.updateTime)
    }
    function open() { BOAT.charge_service.open(_displayCharge) }
    function init() {
        BOAT.event_handler.on($("#popupMain"),
            {
                "event": "click",
                "selector": "#chargeInstructAmtKey",
                "func": function () {
                    BOAT.key_controller.open({
                        "isNumericKey": true,
                        "isAmount": true,
                        "zeroCount": 3,
                        "invokerItemId": "chargeInstructAmt",
                        "maxLength": 4
                    })
                }
            });
        BOAT.event_handler.on($("#popupMain"), {
            "event": "click",
            "selector": "#chargeBetPasswordKey",
            "func": function () {
                BOAT.key_controller.open({
                    "invokerItemId": "chargeBetPassword",
                    "maxLength": 10
                })
            }
        });
        BOAT.event_handler.on($("#popupMain"), {
            "event": "click",
            "selector": "#executeCharge",
            "func": function () {
                BOAT.chargecomp_controller.open(_useBankCode)
            }
        });
        BOAT.event_handler.on($("#popupMain"), {
            "event": "click",
            "selector": "#closeCharge",
            "func": function () {
                BOAT.screenId.setScreenIdClose();
                $("#popupMain").fadeOut("first");
                BOAT.screen.unloadOverlay()
            }
        })
    } return { init: init, open: open }
} ();




'use strict';
BOAT.ajax = function () {
    var _contextPath;
    var _centerNo;
    var _timeout;
    var _isAjax = false;
    var NOT_TARGET = ["number", "string", "null", "undefined", "function"];
    function _ajax(param, done, fail, always) {
        var randomID = BOAT.common_utils.generateRandomID();
        var url = _contextPath + BOAT.common_utils.getProperty(param.urlKey);
        url = url + "?";
        url = url + "cid=" + _centerNo;
        url = url + "&";
        url = url + "r=" + randomID;
        var requestData = param.data;
        requestData.screenFrom = $(":hidden[name='screenFrom']").val();
        if (param.operationKbn) requestData.operationKbn =
            param.operationKbn;
        if (param.checkDoubleAction) requestData.token = $(":hidden[name='token']").val();
        $.ajax(url, { "type": "POST", "data": $.param(requestData), "timeout": _timeout, "dataType": "json" }).done(function (data) { done(_convertObjectKey(data)) }).fail(function (jqXHR) { fail(jqXHR) }).always(function () { always() })
    }
    function _fail(jqXHR) {
        var statusCode = jqXHR.status;
        var statusText = jqXHR.statusText;
        var STATUS_404 = 404;
        var STATUS_500 = 500;
        var MSGCODE_00401 = "00401";
        var MSGCODE_00404 = "00404";
        var param;
        if (jqXHR.responseJSON !==
            undefined) if (jqXHR.responseJSON.param !== undefined) param = jqXHR.responseJSON.param;
        if (statusText === "timeout") param = { "messageCode": MSGCODE_00404, "datetime": moment().format("YYYYMMDDHHmmss"), "screenType": BOAT.popup_controller.SCREEN_TYPE.POPUP_OK };
        if (statusCode === STATUS_500 || statusCode === STATUS_404 || param === undefined) param = { "messageCode": MSGCODE_00401, "datetime": moment().format("YYYYMMDDHHmmss"), "screenType": BOAT.popup_controller.SCREEN_TYPE.POPUP_LOGOUT };
        BOAT.popup_controller.open(param)
    }
    function init() {
        _contextPath =
            $("meta[name='contextPath']").attr("content");
        var csrfToken = $("meta[name='_csrf_token']").attr("content");
        _centerNo = $("meta[name='centerNo']").attr("content");
        var csrfHeaderName = $("meta[name='_csrf_headerName']").attr("content");
        $(document).ajaxSend(function (event, xhr) { xhr.setRequestHeader(csrfHeaderName, csrfToken) });
        _timeout = BOAT.common_utils.parseNumber(BOAT.common_utils.getProperty("ajax_timeout"))
    }
    function ajaxCommunication(param) {
        _isAjax = true;
        _ajax(
            param,
            function (data) {
                if (param.callbackService) BOAT.event_handler.createHandler(param.callbackService, true)(data);
                if (param.callbackControl) BOAT.event_handler.createHandler(param.callbackControl, true)(data)
            },
            function (jqXHR) {
                _fail(jqXHR);
                if (param.callbackFail) BOAT.event_handler.createHandler(param.callbackFail, true)(jqXHR)
            },
            function () {
                _isAjax = false;
                BOAT.screen.modStatusNormal()
            })
    }
    function ajaxCommunicationJustSend(param) {
        _ajax(
            param,
            function () { },
            function () { },
            function () { if (param.callback) BOAT.event_handler.createHandler(param.callback, true)({}) }
        )
    }
    function isAjax() {
        return _isAjax
    }
    function _rename(data, key) {
        if ($.type(data[key]) === "boolean" && $.type(key) === "string") {
            var temp = data[key];
            delete data[key];
            data[function () { return "is" + key.substring(0, 1).toUpperCase() } () + key.substring(1, key.length)] = temp
        }
    }
    function _convertObjectKey(data) {
        if ($.inArray($.type(data), NOT_TARGET) === -1) $.each(data, function (key) {
            _rename(data, key);
            _convertObjectKey(data[key])
        });
        return data
    } return {
        init: init,
        ajaxCommunication: ajaxCommunication,
        ajaxCommunicationJustSend: ajaxCommunicationJustSend,
        isAjax: isAjax
    }
} ();

/*
SQLyog Enterprise - MySQL GUI
MySQL - 8.0.32 
*********************************************************************
*/
/*!40101 SET NAMES utf8 */;

insert into `lims_appfunction` (`id`, `name`, `priv`, `link`, `desc`, `parentid`) values('1','实验室功能','lims.labfunction','/lims/index','实验室功能','0');
insert into `lims_appfunction` (`id`, `name`, `priv`, `link`, `desc`, `parentid`) values('2','循环excel处理','lims.cycleexcel','/lims/cycles','处理循环excel数据','1');
insert into `lims_appfunction` (`id`, `name`, `priv`, `link`, `desc`, `parentid`) values('3','倍率excel处理','lims.crateexcel','/lims/crate','处理倍率excel','1');
insert into `lims_appfunction` (`id`, `name`, `priv`, `link`, `desc`, `parentid`) values('4','搜索循环记录','lims.cyclesummary','/lims/cyclesummary','根据条件搜索驯悍记录','1');
insert into `lims_appfunction` (`id`, `name`, `priv`, `link`, `desc`, `parentid`) values('5','条码搜索循环记录','lims.cyclebybarcode','/lims/cyclebybarcode','根据条码搜索循环记录','1');
insert into `lims_appfunction` (`id`, `name`, `priv`, `link`, `desc`, `parentid`) values('6','HR功能','lims.hrfunction','/lims/index','HR功能','0');
insert into `lims_appfunction` (`id`, `name`, `priv`, `link`, `desc`, `parentid`) values('7','入职时间维护','lims.joindate','/lims/vhrjoindate','维护入职时间','6');
insert into `lims_appfunction` (`id`, `name`, `priv`, `link`, `desc`, `parentid`) values('8','生成邮件签名','lims.signature','/lims/signature','生成邮件签名','6');
insert into `lims_appfunction` (`id`, `name`, `priv`, `link`, `desc`, `parentid`) values('9','出入库管理','lims.wms','/lims/index','出入库管理','0');
insert into `lims_appfunction` (`id`, `name`, `priv`, `link`, `desc`, `parentid`) values('10','电芯类型维护','lims.celltype','/lims/celltype','电芯类型维护','9');
insert into `lims_appfunction` (`id`, `name`, `priv`, `link`, `desc`, `parentid`) values('11','电芯来源维护','lims.cellsource','/lims/cellsource','电芯来源维护','9');
insert into `lims_appfunction` (`id`, `name`, `priv`, `link`, `desc`, `parentid`) values('12','电芯入库','lims.stockin','/lims/stockin','电芯入库','9');
insert into `lims_appfunction` (`id`, `name`, `priv`, `link`, `desc`, `parentid`) values('13','电芯出库','lims.stockout','/lims/stockout','电芯出库','9');
insert into `lims_appfunction` (`id`, `name`, `priv`, `link`, `desc`, `parentid`) values('14','电芯库存查询','lims.stockquery','/lims/stockquery','电芯库存查询','9');
insert into `lims_appfunction` (`id`, `name`, `priv`, `link`, `desc`, `parentid`) values('15','保密资源信息','lims.resource','/lims/index','资源信息','0');
insert into `lims_appfunction` (`id`, `name`, `priv`, `link`, `desc`, `parentid`) values('16','管理资源类型','lims.resourcetype','/lims/setresourcetype','资源类型维护','15');
insert into `lims_appfunction` (`id`, `name`, `priv`, `link`, `desc`, `parentid`) values('17','资源维护','lims.codewrite','/lims/setresource','资源维护','15');
insert into `lims_appfunction` (`id`, `name`, `priv`, `link`, `desc`, `parentid`) values('18','查看资源','lims.coderead','/lims/readresource','资源查看','15');
insert into `lims_appfunction` (`id`, `name`, `priv`, `link`, `desc`, `parentid`) values('19','发送工资条','lims.sendsalary','/lims/sendsalary','发送工资条','6');
insert into `lims_appfunction` (`id`, `name`, `priv`, `link`, `desc`, `parentid`) values('20','测试中心库存管理','lims.uatwms','/lims/index','测试中心库存管理','0');
insert into `lims_appfunction` (`id`, `name`, `priv`, `link`, `desc`, `parentid`) values('21','电芯类型维护','lims.uatcelltype','/lims/uatcelltype','电芯类型维护','20');
insert into `lims_appfunction` (`id`, `name`, `priv`, `link`, `desc`, `parentid`) values('22','电芯入库','lims.uatstockin','/lims/uatstockin','电芯入库','20');
insert into `lims_appfunction` (`id`, `name`, `priv`, `link`, `desc`, `parentid`) values('23','电芯出库','lims.uatstockout','/lims/uatstockout','电芯出库','20');
insert into `lims_appfunction` (`id`, `name`, `priv`, `link`, `desc`, `parentid`) values('24','电芯库存查询','lims.uatstockquery','/lims/uatstockquery','电芯库存查询','20');
insert into `lims_appfunction` (`id`, `name`, `priv`, `link`, `desc`, `parentid`) values('25','查询已还回电芯','lims.getuatstockoutreturn','/lims/getuatstockoutreturn','查询已还回电芯','20');

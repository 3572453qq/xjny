/*
SQLyog Enterprise - MySQL GUI
MySQL - 8.0.32 
*********************************************************************
*/
/*!40101 SET NAMES utf8 */;

insert into `lims_appfunction` (`id`, `name`, `priv`, `link`, `desc`, `parentid`) values('2','循环excel处理','cycleexcel','/lims/cycles','处理循环excel数据','1');
insert into `lims_appfunction` (`id`, `name`, `priv`, `link`, `desc`, `parentid`) values('1','实验室功能','labfunction','/lims/index','实验室功能','0');
insert into `lims_appfunction` (`id`, `name`, `priv`, `link`, `desc`, `parentid`) values('3','倍率excel处理','crateexcel','/lims/crate','处理倍率excel','1');
insert into `lims_appfunction` (`id`, `name`, `priv`, `link`, `desc`, `parentid`) values('4','搜索循环记录','cyclesummary','/lims/cyclesummary','根据条件搜索驯悍记录','1');
insert into `lims_appfunction` (`id`, `name`, `priv`, `link`, `desc`, `parentid`) values('5','条码搜索循环记录','cyclebybarcode','/lims/cyclebybarcode','根据条码搜索循环记录','1');
insert into `lims_appfunction` (`id`, `name`, `priv`, `link`, `desc`, `parentid`) values('6','HR功能','hrfunction','/lims/index','HR功能','0');
insert into `lims_appfunction` (`id`, `name`, `priv`, `link`, `desc`, `parentid`) values('7','入职时间维护','joindate','/lims/vhrjoindate','维护入职时间','6');

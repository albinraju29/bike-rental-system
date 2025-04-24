-- phpMyAdmin SQL Dump
-- version 3.3.9
-- http://www.phpmyadmin.net
--
-- Host: localhost
-- Generation Time: Mar 22, 2022 at 02:45 PM
-- Server version: 5.5.8
-- PHP Version: 5.3.5

SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;

--
-- Database: `bike`
--

-- --------------------------------------------------------

--
-- Table structure for table `bikes`
--

CREATE TABLE IF NOT EXISTS `bikes` (
  `bid` int(50) NOT NULL AUTO_INCREMENT,
  `bikenum` varchar(50) NOT NULL,
  `bikemodel` varchar(50) NOT NULL,
  `station` varchar(50) NOT NULL,
  `rstation` varchar(50) NOT NULL,
  `status` varchar(50) NOT NULL,
  PRIMARY KEY (`bid`)
) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=8 ;

--
-- Dumping data for table `bikes`
--

INSERT INTO `bikes` (`bid`, `bikenum`, `bikemodel`, `station`, `rstation`, `status`) VALUES
(5, 'KL6789', 'samp2', 'kacheripady', '', '0'),
(6, 'kl07 9898', 'yamaha', 'MG', '', '0'),
(7, 'KL89765', 'honda', 'MG', '', '0');

-- --------------------------------------------------------

--
-- Table structure for table `booking`
--

CREATE TABLE IF NOT EXISTS `booking` (
  `bkid` int(50) NOT NULL AUTO_INCREMENT,
  `duration` varchar(50) NOT NULL,
  `strtstation` varchar(50) NOT NULL,
  `endstation` varchar(50) NOT NULL,
  `bikenum` varchar(50) NOT NULL,
  `userid` int(50) NOT NULL,
  `date` varchar(50) NOT NULL,
  `rtrn` int(50) NOT NULL,
  PRIMARY KEY (`bkid`)
) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=44 ;

--
-- Dumping data for table `booking`
--

INSERT INTO `booking` (`bkid`, `duration`, `strtstation`, `endstation`, `bikenum`, `userid`, `date`, `rtrn`) VALUES
(1, '2', '1', '2', '0', 0, '', 0),
(2, '3', '1', '2', '0', 2, '', 0),
(3, '1', '1', '2', '1', 0, '', 0),
(4, '4', '1', '2', 'kj890', 0, '2022-02-13', 0),
(5, '6', '1', '2', 'kl9843', 1, '2022-02-13', 0),
(6, '3', '1', '2', 'kl98765', 2, '2022-02-13', 0),
(7, '6', '1', '2', 'kl9843', 1, '2022-02-13', 0),
(8, '3', '1', '2', 'kl98765', 2, '2022-02-13', 0),
(9, '6', '1', '2', 'kl9843', 1, '2022-02-13', 0),
(10, '3', '1', '2', 'kl98765', 2, '2022-02-13', 0),
(11, '6', '1', '2', 'kl9843', 1, '2022-02-13', 0),
(12, '3', '1', '2', 'kl98765', 2, '2022-02-14', 0),
(13, '6', '1', '2', 'kl9843', 1, '2022-02-14', 0),
(14, '3', '1', '2', 'kl98765', 2, '2022-02-14', 0),
(15, '6', '1', '2', 'kl9843', 1, '2022-02-14', 0),
(16, '3', '1', '2', 'kl98765', 2, '2022-02-14', 0),
(17, '6', '1', '2', 'kl9067', 1, '2022-02-14', 0),
(18, '3', '2', '1', 'kl98765', 2, '2022-02-13', 0),
(19, '6', '2', '1', 'kl9843', 1, '2022-02-13', 0),
(20, '1', '2', '1', 'kl98765', 0, '2022-02-13', 0),
(21, '6', '2', '1', 'kl9843', 1, '2022-02-13', 0),
(22, '5', '2', '1', 'kl98765', 0, '2022-02-14', 0),
(23, '6', '2', '1', 'kl9843', 1, '2022-02-14', 0),
(24, '3', '2', '1', 'kl98765', 2, '2022-02-14', 0),
(25, '3', '2', '1', 'kl9843', 2, '2022-02-14', 0),
(26, '4', '2', '1', 'kl98765', 0, '2022-02-14', 0),
(27, '6', '2', '1', 'kl9067', 1, '2022-02-14', 0),
(28, '3', '2', '1', 'kl98765', 2, '2022-02-14', 0),
(29, '6', '2', '1', 'kl9843', 1, '2022-02-14', 0),
(30, '4', 'MG', 'kacheripady', 'kl89765', 2, '2022-03-07 ', 0),
(31, '19', '1', '2', 'KL6789', 2, '2022-03-07 ', 0),
(32, '20', '1', '2', 'KL6789', 2, '2022-03-07 ', 0),
(33, '20', '1', '2', 'KL6789', 2, '2022-03-07 ', 0),
(34, '19', '1', '2', 'KL6789', 2, '2022-03-07 ', 0),
(35, '20', '1', '2', 'KL6789', 2, '2022-03-07 ', 0),
(36, '19', '2', '1', 'KL6789', 2, '2022-03-07 ', 0),
(37, '4', '1', '2', 'kl678537', 2, '2022-03-07 ', 0),
(38, '1', '1', '2', 'kl07 9898', 4, '2022-03-14 04:38:43.072509', 1),
(40, '4', '1', '2', 'kl07 9898', 5, '2022-03-16 19:10:32.921976', 1),
(41, '1', '1', '2', 'KL6789', 4, '2022-03-17 17:51:04.163530', 0),
(42, '4', '1', '2', 'KL89765', 6, '2022-03-22 19:51:32.614627', 0),
(43, '5', '2', '1', 'kl07 9898', 6, '2022-03-22 20:10:46.547493', 0);

-- --------------------------------------------------------

--
-- Table structure for table `feedback`
--

CREATE TABLE IF NOT EXISTS `feedback` (
  `fid` int(50) NOT NULL AUTO_INCREMENT,
  `date` varchar(50) NOT NULL,
  `feedback` varchar(50) NOT NULL,
  `reply` varchar(50) NOT NULL,
  `uid` int(50) NOT NULL,
  PRIMARY KEY (`fid`)
) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=4 ;

--
-- Dumping data for table `feedback`
--

INSERT INTO `feedback` (`fid`, `date`, `feedback`, `reply`, `uid`) VALUES
(1, '13-02-2022', 'good', '', 1),
(2, '2022-02-14 00:59:40.229936', 'dsdsfs', '', 2),
(3, '2022-03-14 04:52:41.939303', 'byebye', '', 4);

-- --------------------------------------------------------

--
-- Table structure for table `login`
--

CREATE TABLE IF NOT EXISTS `login` (
  `username` varchar(50) NOT NULL,
  `password` varchar(50) NOT NULL,
  `utype` varchar(50) NOT NULL,
  `status` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `login`
--

INSERT INTO `login` (`username`, `password`, `utype`, `status`) VALUES
('admin', 'admin', 'admin', ''),
('SANEM', 'sanem', 'user', 'approved'),
('fasil', 'fasil', 'user', 'approved'),
('jake', 'jakejake', 'user', 'approved'),
('mitty', 'reshmareshma', 'user', 'approved'),
('eshal', 'eshal', 'user', 'approved');

-- --------------------------------------------------------

--
-- Table structure for table `predict`
--

CREATE TABLE IF NOT EXISTS `predict` (
  `count` int(50) NOT NULL,
  `sid` int(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `predict`
--

INSERT INTO `predict` (`count`, `sid`) VALUES
(24, 1),
(13, 2),
(1, 0);

-- --------------------------------------------------------

--
-- Table structure for table `station`
--

CREATE TABLE IF NOT EXISTS `station` (
  `sid` int(50) NOT NULL AUTO_INCREMENT,
  `stationname` varchar(50) NOT NULL,
  `place` varchar(50) NOT NULL,
  `no_of_bikes` int(20) NOT NULL,
  PRIMARY KEY (`sid`)
) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=3 ;

--
-- Dumping data for table `station`
--

INSERT INTO `station` (`sid`, `stationname`, `place`, `no_of_bikes`) VALUES
(1, 'MG', 'kochi', 9),
(2, 'kacheripady', 'kochi', 23);

-- --------------------------------------------------------

--
-- Table structure for table `user_register`
--

CREATE TABLE IF NOT EXISTS `user_register` (
  `uid` int(50) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `phone` varchar(50) NOT NULL,
  `address` varchar(50) NOT NULL,
  `aadhar` varchar(50) NOT NULL,
  `age` int(50) NOT NULL,
  `email` varchar(50) NOT NULL,
  `password` varchar(50) NOT NULL,
  `place` varchar(50) NOT NULL,
  `district` varchar(50) NOT NULL,
  `pincode` int(50) NOT NULL,
  `status` varchar(50) NOT NULL,
  PRIMARY KEY (`uid`)
) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=8 ;

--
-- Dumping data for table `user_register`
--

INSERT INTO `user_register` (`uid`, `name`, `phone`, `address`, `aadhar`, `age`, `email`, `password`, `place`, `district`, `pincode`, `status`) VALUES
(1, 'SANEM', '987654323', 'jan villa', '', 12, 'jan@gmail.com', 'sanem', 'kochi', 'ekm', 682023, 'approved'),
(2, 'fasil', '987654323', 'fasil villa', '', 12, 'jan@gmail.com', 'fasil', 'kochi', 'ekm', 682023, 'approved'),
(4, 'jake', '2147483647', 'jake villa', '', 13, 'jake@gmail.com', 'jakejake', 'kochi', 'ernakulam', 682023, 'approved'),
(5, 'mitty', '9876543232', 'mitty villa', '', 34, 'mittykayalil30@gmail.com', 'reshmareshma', 'kochi', 'ernakulam', 682023, 'approved'),
(6, 'eshal', '8907658907', 'sajila villa', '90876543212', 45, 'reshmajameskj1998@gmail.com', 'eshal', 'ernakulam', 'ernakulam', 682023, 'approved');

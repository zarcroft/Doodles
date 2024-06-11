-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Hôte : 127.0.0.1
-- Généré le : mar. 11 juin 2024 à 20:57
-- Version du serveur : 10.4.32-MariaDB
-- Version de PHP : 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de données : `doodle`
--

-- --------------------------------------------------------

--
-- Structure de la table `centre`
--

CREATE TABLE `centre` (
  `IDCentre` int(11) NOT NULL,
  `Centre` varchar(50) DEFAULT NULL,
  `Ville` varchar(50) DEFAULT NULL,
  `Adresse` varchar(50) DEFAULT NULL,
  `CodePostale` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Structure de la table `classe`
--

CREATE TABLE `classe` (
  `IDClasse` int(11) NOT NULL,
  `Classe` varchar(50) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `classe`
--

INSERT INTO `classe` (`IDClasse`, `Classe`) VALUES
(1, 'Licence RGI'),
(2, 'BTS SN');

-- --------------------------------------------------------

--
-- Structure de la table `compteeleve`
--

CREATE TABLE `compteeleve` (
  `IdCompteEleve` int(11) NOT NULL,
  `Pseudo` varchar(50) DEFAULT NULL,
  `MotDePasse` varchar(50) DEFAULT NULL,
  `IdEleve` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `compteeleve`
--

INSERT INTO `compteeleve` (`IdCompteEleve`, `Pseudo`, `MotDePasse`, `IdEleve`) VALUES
(1, 'flob', 'abcd', 1);

-- --------------------------------------------------------

--
-- Structure de la table `compteformateur`
--

CREATE TABLE `compteformateur` (
  `IDCompteFormateur` int(11) NOT NULL,
  `Pseudo` varchar(50) DEFAULT NULL,
  `MotDePasse` varchar(50) DEFAULT NULL,
  `IdFormateur` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `compteformateur`
--

INSERT INTO `compteformateur` (`IDCompteFormateur`, `Pseudo`, `MotDePasse`, `IdFormateur`) VALUES
(1, 'bidule-a', 'abcd', 1),
(2, 'machin-b', 'abcd', 2),
(4, 'eazy', 'AOUAI', 4);

-- --------------------------------------------------------

--
-- Structure de la table `disponibilite`
--

CREATE TABLE `disponibilite` (
  `IdDisponibilite` int(11) NOT NULL,
  `DateDebut` datetime DEFAULT NULL,
  `DateFin` datetime DEFAULT NULL,
  `Titres` varchar(255) DEFAULT NULL,
  `IdFormateur` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `disponibilite`
--

INSERT INTO `disponibilite` (`IdDisponibilite`, `DateDebut`, `DateFin`, `Titres`, `IdFormateur`) VALUES
(10, '2024-04-02 09:00:00', '2024-04-04 13:30:00', 'test', 1),
(11, '2024-04-15 08:00:00', '2024-04-15 18:00:00', 'test', 1),
(12, '2024-04-29 08:00:00', '2024-04-29 13:30:00', 'RDV', 1),
(15, '2024-05-02 08:00:00', '2024-05-02 13:30:00', 'test', 1),
(16, '2024-05-02 14:30:00', '2024-05-02 17:30:00', 'oui', 1),
(17, '2024-04-29 08:30:00', '2024-04-29 12:00:00', 'sisi', 2),
(18, '2024-06-12 09:00:00', '2024-06-12 12:00:00', 'test', 1);

-- --------------------------------------------------------

--
-- Structure de la table `eleve`
--

CREATE TABLE `eleve` (
  `IdEleve` int(11) NOT NULL,
  `Nom` varchar(50) DEFAULT NULL,
  `Prenom` varchar(50) DEFAULT NULL,
  `Email` varchar(50) DEFAULT NULL,
  `Telephone` int(11) DEFAULT NULL,
  `IDClasse` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `eleve`
--

INSERT INTO `eleve` (`IdEleve`, `Nom`, `Prenom`, `Email`, `Telephone`, `IDClasse`) VALUES
(1, 'berhault', 'florian', 'flo@flob.com', 645256599, 1);

-- --------------------------------------------------------

--
-- Structure de la table `formateur`
--

CREATE TABLE `formateur` (
  `IdFormateur` int(11) NOT NULL,
  `Nom` varchar(50) DEFAULT NULL,
  `Prenom` varchar(50) DEFAULT NULL,
  `Email` varchar(50) DEFAULT NULL,
  `Telephone` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `formateur`
--

INSERT INTO `formateur` (`IdFormateur`, `Nom`, `Prenom`, `Email`, `Telephone`) VALUES
(1, 'bidule', 'aaa', 'florian.berhault07@gmail.com', 245987121),
(2, 'machin', 'bbb', 'vincent.herrera931@gmail.com', 658788832),
(4, 'test', 'test', 'testte@test', 606060606);

-- --------------------------------------------------------

--
-- Structure de la table `formation`
--

CREATE TABLE `formation` (
  `IDClasse` int(11) NOT NULL,
  `IdFormateur` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `formation`
--

INSERT INTO `formation` (`IDClasse`, `IdFormateur`) VALUES
(1, 1),
(1, 2);

-- --------------------------------------------------------

--
-- Structure de la table `reservation`
--

CREATE TABLE `reservation` (
  `IdReservation` int(11) NOT NULL,
  `HeureDebut` datetime DEFAULT NULL,
  `HeureFin` datetime DEFAULT NULL,
  `Titres` varchar(255) DEFAULT NULL,
  `Commentaires` varchar(255) DEFAULT NULL,
  `IdCompteEleve` int(11) NOT NULL,
  `IdFormateur` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `reservation`
--

INSERT INTO `reservation` (`IdReservation`, `HeureDebut`, `HeureFin`, `Titres`, `Commentaires`, `IdCompteEleve`, `IdFormateur`) VALUES
(58, '2024-05-01 11:30:00', '2024-05-01 12:00:00', 'test', 'test', 1, 1),
(60, '2024-05-02 10:00:00', '2024-05-02 10:30:00', '', 'sisi', 1, 1),
(61, '2024-05-01 10:00:00', '2024-05-01 10:30:00', 'test', 'te', 1, 1),
(62, '2024-05-01 09:00:00', '2024-05-01 09:30:00', '', '', 1, 1),
(63, '2024-05-02 09:00:00', '2024-05-02 09:30:00', '', '', 1, 1),
(64, '2024-05-02 09:30:00', '2024-05-02 10:00:00', '', '', 1, 1),
(65, '2024-05-01 14:00:00', '2024-05-01 14:30:00', '', '', 1, 1),
(66, '2024-05-01 13:30:00', '2024-05-01 14:00:00', '', '', 1, 1),
(67, '2024-05-01 12:30:00', '2024-05-01 13:00:00', '', '', 1, 1),
(68, '2024-05-01 12:00:00', '2024-05-01 12:30:00', '', '', 1, 1),
(70, '2024-06-12 10:30:00', '2024-06-12 11:00:00', 'berhault florian', 'test', 1, 1);

--
-- Index pour les tables déchargées
--

--
-- Index pour la table `centre`
--
ALTER TABLE `centre`
  ADD PRIMARY KEY (`IDCentre`);

--
-- Index pour la table `classe`
--
ALTER TABLE `classe`
  ADD PRIMARY KEY (`IDClasse`);

--
-- Index pour la table `compteeleve`
--
ALTER TABLE `compteeleve`
  ADD PRIMARY KEY (`IdCompteEleve`),
  ADD KEY `IdEleve` (`IdEleve`);

--
-- Index pour la table `compteformateur`
--
ALTER TABLE `compteformateur`
  ADD PRIMARY KEY (`IDCompteFormateur`),
  ADD KEY `IdFormateur` (`IdFormateur`);

--
-- Index pour la table `disponibilite`
--
ALTER TABLE `disponibilite`
  ADD PRIMARY KEY (`IdDisponibilite`),
  ADD KEY `IdFormateur` (`IdFormateur`);

--
-- Index pour la table `eleve`
--
ALTER TABLE `eleve`
  ADD PRIMARY KEY (`IdEleve`),
  ADD KEY `IDClasse` (`IDClasse`);

--
-- Index pour la table `formateur`
--
ALTER TABLE `formateur`
  ADD PRIMARY KEY (`IdFormateur`);

--
-- Index pour la table `formation`
--
ALTER TABLE `formation`
  ADD PRIMARY KEY (`IDClasse`,`IdFormateur`),
  ADD KEY `formation_ibfk_2` (`IdFormateur`);

--
-- Index pour la table `reservation`
--
ALTER TABLE `reservation`
  ADD PRIMARY KEY (`IdReservation`),
  ADD KEY `IdCompteEleve` (`IdCompteEleve`),
  ADD KEY `IdFormateur` (`IdFormateur`);

--
-- AUTO_INCREMENT pour les tables déchargées
--

--
-- AUTO_INCREMENT pour la table `centre`
--
ALTER TABLE `centre`
  MODIFY `IDCentre` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT pour la table `classe`
--
ALTER TABLE `classe`
  MODIFY `IDClasse` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT pour la table `compteeleve`
--
ALTER TABLE `compteeleve`
  MODIFY `IdCompteEleve` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT pour la table `compteformateur`
--
ALTER TABLE `compteformateur`
  MODIFY `IDCompteFormateur` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT pour la table `disponibilite`
--
ALTER TABLE `disponibilite`
  MODIFY `IdDisponibilite` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=19;

--
-- AUTO_INCREMENT pour la table `eleve`
--
ALTER TABLE `eleve`
  MODIFY `IdEleve` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT pour la table `formateur`
--
ALTER TABLE `formateur`
  MODIFY `IdFormateur` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT pour la table `reservation`
--
ALTER TABLE `reservation`
  MODIFY `IdReservation` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=71;

--
-- Contraintes pour les tables déchargées
--

--
-- Contraintes pour la table `compteeleve`
--
ALTER TABLE `compteeleve`
  ADD CONSTRAINT `compteeleve_ibfk_1` FOREIGN KEY (`IdEleve`) REFERENCES `eleve` (`IdEleve`) ON DELETE CASCADE;

--
-- Contraintes pour la table `compteformateur`
--
ALTER TABLE `compteformateur`
  ADD CONSTRAINT `compteformateur_ibfk_1` FOREIGN KEY (`IdFormateur`) REFERENCES `formateur` (`IdFormateur`) ON DELETE CASCADE;

--
-- Contraintes pour la table `disponibilite`
--
ALTER TABLE `disponibilite`
  ADD CONSTRAINT `disponibilite_ibfk_1` FOREIGN KEY (`IdFormateur`) REFERENCES `formateur` (`IdFormateur`) ON DELETE CASCADE;

--
-- Contraintes pour la table `eleve`
--
ALTER TABLE `eleve`
  ADD CONSTRAINT `eleve_ibfk_1` FOREIGN KEY (`IDClasse`) REFERENCES `classe` (`IDClasse`) ON DELETE CASCADE;

--
-- Contraintes pour la table `formation`
--
ALTER TABLE `formation`
  ADD CONSTRAINT `formation_ibfk_1` FOREIGN KEY (`IDClasse`) REFERENCES `classe` (`IDClasse`) ON DELETE CASCADE,
  ADD CONSTRAINT `formation_ibfk_2` FOREIGN KEY (`IdFormateur`) REFERENCES `formateur` (`IdFormateur`) ON DELETE CASCADE;

--
-- Contraintes pour la table `reservation`
--
ALTER TABLE `reservation`
  ADD CONSTRAINT `reservation_ibfk_1` FOREIGN KEY (`IdCompteEleve`) REFERENCES `compteeleve` (`IdCompteEleve`) ON DELETE CASCADE,
  ADD CONSTRAINT `reservation_ibfk_2` FOREIGN KEY (`IdFormateur`) REFERENCES `formateur` (`IdFormateur`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;

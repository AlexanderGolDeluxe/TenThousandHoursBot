"""Работа с навыками и пользователем"""
from datetime import time
from aiogram.types import User
from typing import List, Tuple, NamedTuple

from db import db


class Skill(NamedTuple):
    """Структура навыка"""
    id: int
    owner_id: int
    name: str
    spent_hours: float
    description: str


class Skills:
    def __init__(self, user_id: int) -> None:
        self.user_id = user_id
        self.table = "skills"
        self._skills = self._load_skills()

    def _load_skills(self) -> List[Skill]:
        """Возвращает справочник навыков из БД"""
        where_param = dict(owner_id=self.user_id)
        rows = db.fetchall(self.table, ["*"], where_param)
        skills = []
        for row in rows:
            skills.append(
                Skill(
                    id=row["id"],
                    owner_id=row["owner_id"],
                    name=row["name"],
                    spent_hours=row["spent_hours"],
                    description=row["description"]
                )
            )
        return skills

    def get_all_skills(self) -> List[Skill]:
        """Возвращает справочник навыков."""
        return self._skills

    def get_skill(self, skill_id: int) -> Skill:
        """Возвращает навык по идентификатору."""
        where_params = dict(
            id=skill_id,
            owner_id=self.user_id
        )
        finded_skills = db.fetchall(
            table=self.table,
            columns=["*"],
            where_params=where_params
        )
        finded_skill = finded_skills[0]
        finded_skill = Skill(
            id=finded_skill["id"],
            owner_id=finded_skill["owner_id"],
            name=finded_skill["name"],
            spent_hours=finded_skill["spent_hours"],
            description=finded_skill["description"]
        )
        return finded_skill

    def check_skill_already_exists(self, skill_name: str) -> Skill:
        """Проверяет существует ли уже навык с таким именем
        и возвращает его, если находит"""
        skill_name = skill_name.lower()
        finded_skills = [
            skill for skill in self._skills
            if skill.name.lower() == skill_name
        ]
        return finded_skills[0] if finded_skills else None

    def create_skill(self, skill_name: str,
        spent_hours: float, description: str = "") -> None:
        """Создаёт новую запись в таблице навыков
        согласно полученным параметрам"""
        column_values = dict(
            owner_id=self.user_id,
            name=skill_name,
            spent_hours=spent_hours,
            description=description
        )
        db.insert(self.table, column_values)

    def add_hours_to_skill(self,
        skill_id: int, new_spent_hours: float) -> float:
        """Добавляет часы к навыку и возврщает новое время"""
        skill = self.get_skill(skill_id)
        new_spent_hours = max(
            skill.spent_hours + new_spent_hours, 0.0
        )
        db.update(
            table=self.table,
            column_values=dict(spent_hours=new_spent_hours),
            where_params=dict(id=skill.id)
        )
        return new_spent_hours

    def delete_skill(self, skill_id: int) -> None:
        """Удаляет навык по указанному идентификатору"""
        skill_data = dict(id=skill_id, owner_id=self.user_id)
        db.delete(self.table, skill_data)


class TTHours_User(User):
    def __init__(self, user_object: User) -> None:
        self.id = user_object.id
        self.is_bot = user_object.is_bot
        self.first_name = user_object.first_name
        self.last_name = user_object.last_name
        self.username = user_object.username
        self.language_code = user_object.language_code
        self.can_join_groups = user_object.can_join_groups
        self.supports_inline_queries = user_object.supports_inline_queries
        self.can_read_all_group_messages = (
            user_object.can_read_all_group_messages)
    
    def check_user_in_db(self) -> None:
        """Проверяет есть ли пользователь в БД,
        если не находит, добавляет его туда"""
        user_row = db.fetchall(
            table="users",
            columns=["*"],
            where_params=dict(user_id=self.id)
        )
        if not user_row:
            user_data = dict(
                user_id=self.id,
                first_name=self.first_name,
                last_name=self.last_name,
                username=self.username,
                language_code=self.language_code
            )
            db.insert("users", user_data)

    def update_notification_time(self, new_time: time) -> None:
        """Устанавливает новое время для напоминания"""
        user_data_for_update = dict(
            is_notification_on=True,
            notification_time=new_time.isoformat("seconds")
        )
        db.update(
            table="users",
            column_values=user_data_for_update,
            where_params=dict(user_id=self.id))

    def manage_notification(self, is_turn_on: bool) -> None:
        """Вкл./Выкл. напоминание"""
        db.update(
            table="users",
            column_values=dict(is_notification_on=is_turn_on),
            where_params=dict(user_id=self.id))

    def check_notification_on(self) -> bool:
        """Проверяет включено ли напоминание"""
        user_rows = db.fetchall(
            table="users",
            columns=["is_notification_on"],
            where_params=dict(user_id=self.id)
        )
        return bool(user_rows[0]["is_notification_on"])

    def get_notification_settings(self) -> Tuple[time, bool]:
        """Возращает данные про напоминание — время и состояние (вкл./выкл.)"""
        user_rows = db.fetchall(
            table="users",
            columns=["is_notification_on", "notification_time"],
            where_params=dict(user_id=self.id)
        )
        user_row = user_rows[0]
        is_notification_on = bool(user_row["is_notification_on"])
        notification_time = (
            time.fromisoformat(user_row["notification_time"])
        )
        return notification_time, is_notification_on

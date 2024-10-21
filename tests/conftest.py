import asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from fastapi import FastAPI
import pytest

engine = create_async_engine("sqlite+aiosqlite://", echo=True)
async_session = async_sessionmaker(engine, expire_on_commit=False)

